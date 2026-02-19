import requests

# ── API 1: ip-api.com — detecta ubicación por IP ────────────────────────────
# Documentación: http://ip-api.com/docs/api:json
def get_location_by_ip() -> dict:
    try:
        r = requests.get("http://ip-api.com/json/", timeout=6)
        d = r.json()
        if d.get("status") == "success":
            return {
                "success": True,
                "city":    d.get("city", ""),
                "region":  d.get("regionName", ""),
                "country": d.get("country", ""),
                "lat":     d.get("lat", 0),
                "lon":     d.get("lon", 0),
            }
        return {"success": False}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── API 2: Nominatim — convierte ciudad en coordenadas ──────────────────────
# Documentación: https://nominatim.org/release-docs/latest/api/Search/
def geocode_city(city: str) -> dict:
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "format": "json", "limit": 1},
            headers={"User-Agent": "SocialInsightPro/1.0"},
            timeout=8,
        )
        results = r.json()
        if results:
            return {
                "success": True,
                "lat":  float(results[0]["lat"]),
                "lon":  float(results[0]["lon"]),
                "name": results[0].get("display_name", city),
            }
        return {"success": False, "error": "Ciudad no encontrada"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── API 3: Overpass (OpenStreetMap) — estadios reales cercanos ───────────────
# Documentación: https://wiki.openstreetmap.org/wiki/Overpass_API
def get_stadiums_near(lat: float, lon: float, radius_km: int = 50) -> list:
    radius_m = radius_km * 1000
    query = f"""
    [out:json][timeout:25];
    (
      node["leisure"="stadium"]["sport"~"soccer|football",i](around:{radius_m},{lat},{lon});
      way["leisure"="stadium"]["sport"~"soccer|football",i](around:{radius_m},{lat},{lon});
      relation["leisure"="stadium"]["sport"~"soccer|football",i](around:{radius_m},{lat},{lon});
      node["leisure"="stadium"](around:{radius_m},{lat},{lon});
      way["leisure"="stadium"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=20,
        )
        elements = r.json().get("elements", [])
        stadiums = []
        seen = set()

        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:es") or tags.get("name:en")
            if not name or name in seen:
                continue
            seen.add(name)

            # coordenadas: nodo directo o centroide de way/relation
            if el["type"] == "node":
                s_lat, s_lon = el.get("lat", lat), el.get("lon", lon)
            else:
                center = el.get("center", {})
                s_lat  = center.get("lat", lat)
                s_lon  = center.get("lon", lon)

            # distancia aproximada en km (Haversine simplificada)
            from math import radians, cos, sin, asin, sqrt
            def haversine(la1, lo1, la2, lo2):
                R = 6371
                dla = radians(la2 - la1)
                dlo = radians(lo2 - lo1)
                a = sin(dla/2)**2 + cos(radians(la1))*cos(radians(la2))*sin(dlo/2)**2
                return round(2 * R * asin(sqrt(a)), 1)

            dist = haversine(lat, lon, s_lat, s_lon)

            stadiums.append({
                "name":     name,
                "lat":      s_lat,
                "lon":      s_lon,
                "distance": dist,
                "capacity": tags.get("capacity", "—"),
                "sport":    tags.get("sport", "football"),
                "website":  tags.get("website") or tags.get("url", ""),
                "operator": tags.get("operator") or tags.get("club", ""),
                "city":     tags.get("addr:city") or tags.get("is_in:city", ""),
                "country":  tags.get("addr:country", ""),
            })

        # Ordenar por distancia
        stadiums.sort(key=lambda s: s["distance"])
        return stadiums[:20]

    except Exception as e:
        return []