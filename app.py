from flask import Flask, redirect, request, session
from ssoready.client import SSOReady

# Do not hard-code or leak your SSOReady API key in production!
#
# In production, instead you should configure a secret SSOREADY_API_KEY
# environment variable. The SSOReady SDK automatically loads an API key from
# SSOREADY_API_KEY.
#
# This key is hard-coded here for the convenience of logging into a test app,
# which is hard-coded to run on http://127.0.0.1:5000. It's only because of
# this very specific set of constraints that it's acceptable to hard-code and
# publicly leak this API key.
ssoready = SSOReady(api_key="ssoready_sk_ephref548qglzv0cmybrnihg3")

app = Flask(__name__)

# This demo uses flask's built-in sessions module to do user sessions, to keep
# things simple. SSOReady works with any stack or session technology you use.
app.secret_key = b'this is just a demo'

# This demo just renders plain old HTML with no client-side JavaScript. This is
# only to keep the demo minimal. SSOReady works with any frontend stack or
# framework you use.
#
# This demo keeps the HTML minimal to keep things as simple as possible here.
@app.route("/")
def index():
    return f"""
    <!doctype html>
    <html>
        <body>
            <h1>Hello, {session.get("email") or "logged-out user"}!</h1>

            <a type="button" href="/logout">Log out</a>

            <!-- submitting this form makes the user's browser do a GET /saml-redirect?email=... -->
            <form method="get" action="/saml-redirect">
                <h2>Log in with SAML</h2>

                <label for="email">Email</label>
                <input id="email" type="email" name="email" placeholder="john.doe@example.com" />

                <button>Submit</button>

                <p>(Try any @example.com or @example.org email address.)</p>
            </form>
        </body>
    </html>
    """

# This is the page users visit when they click on the "Log out" link in this
# demo app. It just resets `email` in `session`, which deletes the user's
# session cookie in this demo.
#
# SSOReady doesn't impose any constraints on how your app's sessions work.
@app.route("/logout")
def logout():
    del session["email"]
    return redirect("/")

# This is the page users visit when they submit the "Log in with SAML" form in
# this demo app.
@app.route("/saml-redirect")
def saml_redirect():
    # To start a SAML login, you need to redirect your user to their employer's
    # particular Identity Provider. This is called "initiating" the SAML login.
    #
    # Use `saml.get_saml_redirect_url` to initiate a SAML login.
    redirect_url = ssoready.saml.get_saml_redirect_url(
        # OrganizationExternalId is how you tell SSOReady which company's
        # identity provider you want to redirect to.
        #
        # In this demo, we identify companies using their domain. This code
        # converts "john.doe@example.com" into "example.com".
        organization_external_id=request.args["email"].split("@")[1]
    ).redirect_url

    # `saml.get_saml_redirect_url` returns an object like this:
    #
    # GetSamlRedirectUrlResponse(redirect_url="https:#...")
    #
    # To initiate a SAML login, you redirect the user to that redirect_url.
    return redirect(redirect_url)

# This is the page SSOReady redirects your users to when they've successfully
# logged in with SAML.
@app.route("/ssoready-callback")
def ssoready_callback():
    # SSOReady gives you a one-time SAML access code under
    # ?saml_access_code=saml_access_code_... in the callback URL's query
    # parameters.
    #
    # You redeem that SAML access code using `saml.redeem_saml_access_code`,
    # which gives you back the user's email address. Then, it's your job to log
    # the user in as that email.
    email = ssoready.saml.redeem_saml_access_code(
        saml_access_code=request.args["saml_access_code"]
    ).email

    # SSOReady works with any stack or session technology you use. In this demo
    # app, we use Flask's built-in sessions module. This code is how
    # `flask.session` does logins.
    session["email"] = email

    # Redirect back to the demo app homepage.
    return redirect("/")
