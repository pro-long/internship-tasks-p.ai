from flask import Flask, request, jsonify
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TMDB_BEARER = os.getenv("TMDB_BEARER")
if not TMDB_BEARER:
    raise RuntimeError("TMDB_BEARER missing in environment")

app = Flask(__name__)

def find_price_gap_pair(nums: list[int], k: int) -> tuple[int, int] | None:
    ans = set()
    value_to_index = {}
    
    for index, value in enumerate(nums):
        if value not in value_to_index:
            value_to_index[value] = []
        value_to_index[value].append(index)
    
    for index, value in enumerate(nums):
        if value<0: diff = value+k
        else: diff = value-k

        if diff in value_to_index:
            for index_diff in value_to_index[diff]:
                if index != index_diff:
                    pair = tuple(sorted([index, index_diff]))
                    ans.add(pair)

    if not ans:
        return None

    ans = sorted(list(ans))
    return ans[0]

@app.post("/api/price-gap-pair")
def price_gap_pair():
    data = request.get_json()
    if not data or "nums" not in data or "k" not in data:
        return jsonify({"error":"nums + k required"}), 400
    
    nums = data["nums"]
    k = data["k"]

    if not isinstance(nums, list) or not isinstance(k, int) or k < 0:
        return jsonify({"error":"invalid input"}), 400

    result = find_price_gap_pair(nums, k)

    if result is None:
        return jsonify({"pair":None,"values":None})

    i,j = result
    return jsonify({"pair":[i,j], "values":[nums[i], nums[j]]})


@app.get("/api/movies")
def movies():
    q = request.args.get("q")
    page = request.args.get("page",1,type=int)

    if not q or q.strip()=="":
        return jsonify({
            "page":page,
            "total_pages":0,
            "total_results":0,
            "results":[]
        })

    headers = {"Authorization": f"Bearer {TMDB_BEARER}", "accept":"application/json"}

    try:
        r = httpx.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"query":q, "page":page},
            headers=headers,
            timeout=5.0
        )
    except:
        return jsonify({"error":"movie api failed"}),502
    
    if r.status_code>=500:
        return jsonify({"error":"upstream failure"}),502
    
    data = r.json()

    results = [{"title":m.get("title"),"director":None} for m in data.get("results",[])]

    return jsonify({
        "page":data.get("page"),
        "total_pages":data.get("total_pages"),
        "total_results":data.get("total_results"),
        "results":results
    })


if __name__ == "__main__":
    app.run(debug=True)