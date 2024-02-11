# Authentication

Authentication works just the same as [shotgun_api3](https://developers.shotgridsoftware.com/python-api/authentication.html),
with the only difference that you are passing in any of the parameters into the
[pyshotgrid.new_site](#pyshotgrid.core.new_site) function.
If you already have a valid instance of [shotgun_api3.Shotgun](https://developers.shotgridsoftware.com/python-api/reference.html#shotgun)
you also pass that into the [pyshotgrid.new_site](#pyshotgrid.core.new_site) function directly.
Or if you put that into code:
```python
# Method A
sg_site_b = pyshotgrid.new_site(base_url='https://example.shotgunstudio.com',
                                script_name='Some User',
                                api_key='$ome_password')

# Method B
sg = shotgun_api3.Shotgun(base_url='https://example.shotgunstudio.com',
                          script_name='Some User',
                          api_key='$ome_password')
sg_site_a = pyshotgrid.new_site(sg)

# Both methods lead to the same outcome.
assert sg_site_a == sg_site_b
```

## Use tk-core for authentication

You can piggy back [SGTK's authentication](https://developers.shotgridsoftware.com/tk-core/authentication.html#authentication)
procedures to make your live a bit easier to start out with `pyshotgrid`. The basic idea is to reuse
the session token from either SG Desktop or SG Create, so you do not need to use another ShotGrid API key.

```python
from tank.authentication import ShotgunAuthenticator
import pyshotgrid

# create an authenticator
sa = ShotgunAuthenticator()

# Get a user object. If the authenticator system has already
# stored a default user belonging to a default shotgun site,
# it will simply return this. Otherwise, it will pop up a UI
# asking the user to log in.
user = sa.get_user()

# now the user object can be used to generate an authenticated
# Shotgun connection.
sg = user.create_sg_connection()

# With this you can generate a new pyshotgrid.SGSite and start working.
sg_site = pyshotgrid.new_site(sg)
```
:::{warning}
Be aware of the following caveats:
- You are running the all Shotgrid CRUD operations with the permissions of the current user in
  SG Desktop/SG Create.
- The session token can expire midway through your script and SGTK will prompt you for your
  credentials again. (Happens roughly once a day.)
:::

Due to this I recommend to use this approach mainly for Developers. It is great for starting out
with the library or quickly running a simple scripts to fix up some things in ShotGrid. Depending
on your goal it can also be used in production environments, but can be limiting.
