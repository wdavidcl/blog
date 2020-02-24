from blog import app
#sometimes you need to CHANGE HOST to 127.0.0.1 for LOCAL RUNING
if __name__ == '__main__':
    #app.run(host='127.0.0.1',port='8000',debug=True)
    app.run(host='0.0.0.0', port='8000', debug=True, use_reloader=False)
