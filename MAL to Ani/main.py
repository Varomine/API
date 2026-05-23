from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="MAL to AniList Converter API")

ANILIST_API_URL = "https://graphql.anilist.co"

QUERY = """
query ($idMal: Int, $type: MediaType) {
  Media (idMal: $idMal, type: $type) {
    id
    title {
      romaji
      english
      native
    }
    type
    siteUrl
    description
  }
}
"""

@app.get("/")
def read_root():
    return {"message": "MAL to AniList API is running!", "usage": "/convert/{mal_id}?type=ANIME"}

@app.get("/convert/{mal_id}")
async def convert_id(mal_id: int, type: str = "ANIME"):
    # ตรวจสอบประเภทว่าเป็น ANIME หรือ MANGA
    media_type = type.upper()
    if media_type not in ["ANIME", "MANGA"]:
        raise HTTPException(status_code=400, detail="Type must be ANIME or MANGA")

    variables = {
        "idMal": mal_id,
        "type": media_type
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                ANILIST_API_URL,
                json={'query': QUERY, 'variables': variables},
                timeout=10.0
            )
            res_data = response.json()

            if response.status_code != 200:
                return {"error": "AniList API Error", "details": res_data}

            if res_data.get("data") and res_data["data"]["Media"]:
                return {
                    "status": "success",
                    "mal_id": mal_id,
                    "anilist_id": res_data["data"]["Media"]["id"],
                    "data": res_data["data"]["Media"]
                }
            else:
                raise HTTPException(status_code=404, detail="Mapping not found for this ID")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
