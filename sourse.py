from flask import Flask, render_template, request
from base import host, user, password, db_name, salt
from functools import partial
from hashlib import pbkdf2_hmac
import pymysql


app = Flask(__name__)

def encryption(password: str) -> str:
    return pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000).hex()

CONNECTION = pymysql.connect(
    host=host,
    port=3306,
    user=user,
    password=password,
    database=db_name,
    cursorclass=pymysql.cursors.DictCursor
)

name_list = list(enumerate(["title", "inform", "product", "settings"], 1))
error_data = "Error - no correct data"
error_password = "Error - no correct password"

@app.route("/")
@app.route("/title", methods=["POST", "GET"])
def sourse1():
    page = partial(render_template, "title.html", last=name_list, digit=1)
    if request.method == "POST":
        info = request.form
        if not (0 < len(info["collection"]) <= 100 and 10 < len(info['password']) < 100):
            return page(error=error_data)
        with CONNECTION.cursor() as cursor:
            cursor.execute(f"""
            SELECT password_hash\
            FROM collection\
            WHERE name_collection = '{info['collection']}'
            """)
            response = cursor.fetchall()
            if response:
                if encryption(info['password']) == response[0]['password_hash']:
                    print(1)
                    return page(base=info['collection'])
                else:
                    return page(error=error_password)
            else:
                cursor.execute(f"""
                INSERT INTO collection(name_collection, password_hash)\
                VALUES ('{request.form['collection']}', '{encryption(password)}');
                """)
                CONNECTION.commit()
    return page()

@app.route("/inform")
def sourse2():
    return render_template("inform.html", last=name_list, digit=2)

@app.route("/product")
def sourse3():
    return render_template("product.html", last=name_list, digit=3)

@app.route("/settings")
def sourse4():
    return render_template("settings.html", last=name_list, digit=4)


    
    
if __name__ == "__main__":
   app.run(debug=True)