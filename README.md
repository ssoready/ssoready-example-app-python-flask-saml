# SSOReady Example App: C# ASP.NET Core with SAML

This repo contains a minimal example app built with Python and
[Flask](https://flask.palletsprojects.com/en/2.3.x/) that supports
[SAML](https://ssoready.com/docs/saml/saml-quickstart) using
[SSOReady](https://ssoready.com/), an
[open-source](https://github.com/ssoready/ssoready) way to add SAML and SCIM
support to your product.

## Running it yourself

To check out this repo yourself, you'll need a working installation of `dotnet`.
Then, run:

```
git clone https://github.com/ssoready/ssoready-example-app-python-flask-saml
cd ssoready-example-app-python-flask-saml

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

flask run
```

Then, visit http://127.0.0.1:5000.

## How it works

There are two steps involved in implementing SAML:

1. Initiating SAML logins, where you redirect the user to their corporate
   identity provider
2. Handling SAML logins, where you log the user in after they've authenticated
   using SAML.

### Initiating SAML logins

In this demo app, initiating SAML logins happens from the `/saml-redirect`
endpoint:

```python
@app.route("/saml-redirect")
def saml_redirect():
    redirect_url = ssoready.saml.get_saml_redirect_url(
        # convert "john.doe@example.com" into "example.com".
        organization_external_id=request.args["email"].split("@")[1]
    ).redirect_url

    return redirect(redirect_url)
```

You initiate a SAML login by calling
[`saml.get_saml_redirect_url`](https://ssoready.com/docs/api-reference/saml/get-saml-redirect-url)
and redirecting to the returned URL.

The
[`organization_external_id`](https://ssoready.com/docs/api-reference/saml/get-saml-redirect-url#request.body.organizationExternalId)
is to tell SSOReady which customer's corporate identity provider you want to
redirect to. In the demo app, we use `example.com` or `example.org` as the
[organization external
ID](https://ssoready.com/docs/ssoready-concepts/organizations#organization-external-id).

### Handling SAML logins

After your user finishes authenticating over SAML, SSOReady will redirect them
back to your application. In this demo app, that callback URL is configured to
be `http://localhost:5293/ssoready-callback`, so you'll get requests that look
like this:

```
GET http://localhost:5293/ssoready-callback?saml_access_code=saml_access_code_...
```

Here's how the demo app handles those requests:

```csharp
app.MapGet("/ssoready-callback", async (HttpContext context, [FromQuery(Name = "saml_access_code")] string samlAccessCode) =>
{
    var redeemResponse = await ssoready.Saml.RedeemSamlAccessCodeAsync(new RedeemSamlAccessCodeRequest
    {
        SamlAccessCode = samlAccessCode
    });

    context.Session.SetString("email", redeemResponse.Email!);
    return Results.Redirect("/");
});
```

You handle a SAML login by calling
[`Saml.RedeemSamlAccessCodeAsync`](https://ssoready.com/docs/api-reference/saml/redeem-saml-access-code)
with the `saml_access_code` query parameter value, and logging the user in from
the `Email` SSOReady returns to you.

And that's it! That's all the code you have to write to add SAML support to your
application.

### Configuring SSOReady

To make this demo app work out of the box, we did some work for you. You'll need
to follow these steps yourself when you integrate SAML into your app.

The steps we took were:

1. We signed up for SSOReady at https://app.ssoready.com.
2. We created an
   [environment](https://ssoready.com/docs/ssoready-concepts/environments), and
   configured its [redirect
   URL](https://ssoready.com/docs/ssoready-concepts/environments#redirect-url)
   to be `http://localhost:5293/ssoready-callback`.
3. We created an [API
   key](https://ssoready.com/docs/ssoready-concepts/environments#api-keys).
   Because this is a demo app, we hard-coded the API key. In production apps,
   you'll instead put that API key secret into an `SSOREADY_API_KEY` environment
   variable on your backend.
4. We created two
   [organizations](https://ssoready.com/docs/ssoready-concepts/organizations),
   both of which use [DummyIDP.com](https://ssoready.com/docs/dummyidp) as their
   "corporate" identity provider:

   - One organization has [external
     ID](https://ssoready.com/docs/ssoready-concepts/organizations#organization-external-id)
     `example.com` and a [domain
     whitelist](https://ssoready.com/docs/ssoready-concepts/organizations#domains)
     of just `example.com`.
   - The second organization has extnernal ID `example.org` and domain whitelist
     `example.org`.

In production, you'll create a separate organization for each company that wants
SAML. Your customers won't be using [DummyIDP.com](https://dummyidp.com); that's
just a SAML testing service that SSOReady offers for free. Your customers will
instead be using vendors including
[Okta](https://www.okta.com/products/single-sign-on-customer-identity/),
[Microsoft
Entra](https://www.microsoft.com/en-us/security/business/microsoft-entra), and
[Google Workspace](https://workspace.google.com/). From your code's perspective,
those vendors will all look exactly the same.

## Next steps

This demo app gives you a crash-course demo of how to implement SAML end-to-end.
If you want to see how this all fits together in greater detail, with every step
described in greater detail, check out the [SAML
quickstart](https://ssoready.com/docs/saml/saml-quickstart) or the rest of the
[SSOReady docs](https://ssoready.com/docs).
