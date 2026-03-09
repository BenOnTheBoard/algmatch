class GenericGeneratorInterface:
    def generate_instance():
        """
        Generates an valid instance of a particular problem. e.g. SM, HRT.
        """
        raise NotImplementedError("Method not implemented")

    def _assert_valid_parameters():
        """
        Conducts a series of checks on setup variables.
        Shows informative errors where issues are located.
        """
        raise NotImplementedError("Method not implemented")

    def _reset_instance():
        """
        Returns each agent's preference list to the empty state.
        """
        raise NotImplementedError("Method not implemented")
