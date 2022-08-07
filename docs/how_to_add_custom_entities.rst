How to add custom entities
==========================

`pyshotgrid` will return any "unknown" entity as "SGEntity" instance to provide minimum
functionality in all cases. However sometimes you might want to add or extend some
functions on entities to make your live easier. `pyshotgrid` lets you do that, by registering
your custom classes to its setup.
Here is an example python script to illustrate what you have to do:

.. code-block:: python
    :caption: example_custom_entity.py

    """
    Add a custom entity to pyshotgrid.

    This script illustrates how you can integrate a custom entity into the pyshotgrid universe.

    Suppose you are using a custom entity called "Episode" which collects shots and sequences in
    projects. It would be nice if pyshotgrid could reflect that and help you get some information
    faster. Furthermore it would be nice if the default SGProject class would get an additional
    function that returns all episodes of the project.

    Here is what you have to do:
    """
    import fnmatch

    import pyshotgrid as pysg


    # Create a class that inherits from "SGEntity" and all the functionality you want to it.
    # In this example we only add a function to get shots from the episode.
    class SGEpisode(pysg.SGEntity):
        """
        An instance of this class represents a single Episode entity in ShotGrid.
        """

        # This is an example implementation of how to retrieve shots from an episode.
        def shots(self, glob_pattern=None):
            """
            :param str|None glob_pattern: A glob to match the shots to return. For example
                                          `TEST_01_*` would return all shots that start with `TEST_01_`.
            :return: All the shots from this project.
            :rtype: list[SGShot]
            """
            sg_shots = self.sg.find('Shot',
                                    # NOTE: The "sg_episode" field is only made up and
                                    # could differ from your setup.
                                    [['sg_episode', 'is', self.to_dict()]],
                                    ['code'])
            if glob_pattern is not None:
                return [pysg.new_entity(self._sg, sg_shot)
                        for sg_shot in sg_shots
                        if fnmatch.fnmatchcase(sg_shot['code'], glob_pattern)]
            else:
                return [pysg.new_entity(self._sg, sg_shot) for sg_shot in sg_shots]


    # To overwrite/add some functionality to one of the default classes you simply inherit from
    # that class and overwrite/add what you deem necessary.
    # In this case we add a very simple function to return all episodes attached to the current project.
    class CustomSGProject(pysg.sg_default_entities.SGProject):
        """
        Custom extension of the default SGProject class to provide additional functionality.
        """

        def episodes(self):
            """
            :return: All episodes of this project.
            :rtype: list[SGEpisode]
            """
            # We simple return all entities from the "sg_episodes" field.
            # NOTE: This field is made up and could differ depending on your setup.
            return self['sg_episodes'].get()


    # To let pyshotgrid know about your custom classes you need to register them like so:
    # This will let pyshotgrid return a SGEpisode instance whenever it encounters
    # a "CustomProjectEntity01" entity.
    pysg.register_pysg_class('CustomProjectEntity01', SGEpisode)

    # This will let pyshotgrid return a CustomSGProject instance whenever it encounters
    # "Project" entity and therefore we overwrite the default behaviour for all new Project instances.
    pysg.register_pysg_class('Project', CustomSGProject)


    # Here is a small example of the above implementations.
    if __name__ == '__main__':

        # connect to a ShotGrid site
        site = pysg.new_site(base_url='https://example.shotgunstudio.com',
                             script_name='Some User',
                             api_key='$ome_password')

        # Get the "test" project
        project = site.project('test')
        # Get all episodes of that project.
        sg_episodes = project.episodes()
        # List the first shot of the first episode.
        print(sg_episodes[0].shots()[0])
