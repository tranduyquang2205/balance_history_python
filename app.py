from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from namabank import Namabank
import sys
import traceback
from api_response import APIResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
    proxy_list: list = None

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
    try:
        nab = Namabank(input.proxy_list)
        balance = nab.get_balance(input.username, input.password,input.account_number)
        return APIResponse.json_format(balance)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)
    
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    from_date: str
    to_date: str
    limit: int
    proxy_list: list = None
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
    try:
        nab = Namabank(input.proxy_list)
        transactions = nab.get_transaction(input.username, input.password,input.account_number,input.from_date,input.to_date,input.limit)
        return APIResponse.json_format(transactions)
    except Exception as e:
        response = str(e)
        print(traceback.format_exc())
        print(sys.exc_info()[2])
        return APIResponse.json_format(response)
    
if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)