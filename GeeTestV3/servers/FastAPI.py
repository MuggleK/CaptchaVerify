from fastapi import FastAPI
import uvicorn
from Geestest import Capt_validate

app = FastAPI()

@app.get("/captcha")
async def read_root(gt: str,challenge:str,proxy=None):
    res = {}
    if gt is None:
      msg = "need gt,challenge param"
      code = 400
      res['msg'] = msg
      res['code'] = code
      res['data'] = []
    elif '{' in gt:
      msg = "参数错误！"
      code = 400
      res['msg'] = msg
      res['code'] = code
      res['data'] = []
    else:
      res = await Capt_validate(gt,challenge,proxy).run()
    return res


if __name__ == '__main__':
    uvicorn.run(app='Api:app', host="0.0.0.0", port=8049, reload=False, debug=False)


