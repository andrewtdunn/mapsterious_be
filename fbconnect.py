def connectFB(request, login_session):
    print "fbconnect()"
    if request.args.get('state') != login_session('state')
        repsonse = make_response(json.dumps('Invalid state parameter.'), 401)
        response.header['Content-type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received as %s" % access token

    app_id = json.loads(open('fb_client'))
