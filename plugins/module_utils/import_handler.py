class MissingZOAUImport(object):
    def __getattr__(self, name):
        def method(*args, **kwargs):
            raise ImportError(
                (
                    "ZOAU is not properly configured for Ansible. Unable to import zoautil_py. "
                    "Ensure environment variables are properly configured in Ansible for use with ZOAU."
                )
            )

        return method
