pyshotgrid vs. shotgun_api3
===========================

To give you an idea where the benefits are and how you should use `pyshotgrid` we can compare
it against `shotgun_api3`.

Suppose you want to print the Sequence names of all the shots in project "foobar".
Here is the what that would look like in `shotgun_api3`:

.. code-block:: python
    :caption: shotgun_api3 example

    import shotgun_api3

    sg = shotgun_api3.Shotgun(base_url='https://example.shotgunstudio.com',
                              script_name='Some User',
                              api_key='$ome_password')

    project = sg.find_one('Project', [['tank_name', 'is', 'foobar']])
    print(project)
    shots = sg.find('Shot',
                    [['project', 'is', project]],
                    ['sg_sequence'])
    for shot in shots:
        print(shot)
        sequence = sg.find_one('Sequence',
                               [['id', 'is', shot['sg_sequence']['id']]],
                               ['code'])
        print(sequence['code'])


And the same in `pyshotgrid`:

.. code-block:: python
    :caption: pyshotgrid example

    import pyshotgrid as pysg

    site = pysg.new_site(base_url='https://example.shotgunstudio.com',
                         script_name='Some User',
                         api_key='$ome_password')

    project = site.project('foobar')
    print(project)
    for shot in project.shots():
        print(shot)
        print(shot["sg_sequence"].get()["code"].get())
