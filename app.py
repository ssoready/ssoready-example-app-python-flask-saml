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
    <html>
        <head>
            <title>SAML Demo App using SSOReady</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body>
            <main class="grid min-h-full place-items-center py-32 px-8">
                <div class="text-center">
                    <h1 class="mt-4 text-balance text-5xl font-semibold tracking-tight text-gray-900 sm:text-7xl">
                        <!-- session["email"] gets populated from /ssoready-callback -->
                        Hello, {session.get("email") or "logged-out user"}!
                    </h1>
                    <p class="mt-6 text-pretty text-lg font-medium text-gray-500 sm:text-xl/8">
                        This is a SAML demo app, built using SSOReady.
                    </p>

                    <!-- submitting this form makes the user's browser do a GET /saml-redirect?email=... -->
                    <form method="get" action="/saml-redirect" class="mt-10 max-w-lg mx-auto">
                        <div class="flex gap-x-4 items-center">
                            <label for="email-address" class="sr-only">Email address</label>
                            <input id="email-address" name="email" class="min-w-0 flex-auto rounded-md border-0 px-3.5 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" value="john.doe@example.com" placeholder="john.doe@example.com">
                            <button type="submit" class="flex-none rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                                Log in with SAML
                            </button>
                            <a href="/logout" class="px-3.5 py-2.5 text-sm font-semibold text-gray-900">
                                Sign out
                            </a>
                        </div>
                        <p class="mt-4 text-sm leading-6 text-gray-900">
                            (Try any @example.com or @example.org email address.)
                        </p>
                    </form>
                </div>
            </main>
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
    # GetSamlRedirectUrlResponse(redirect_url="https://...")
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
