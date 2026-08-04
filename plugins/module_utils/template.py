# Copyright (c) IBM Corporation 2022, 2026
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import tempfile
from os import path

from ansible.module_utils._text import to_native
from ansible.module_utils.parsing.convert_bool import boolean

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingImport,
)

# This module is to be used locally, so jinja2 only needs to be installed in the
# controller, but Ansible sanity testing simulates what would happen if a managed
# node tried to use this module_util, hence the use of MissingImport.
try:
    import jinja2
except Exception:
    jinja2 = MissingImport("jinja2")

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import encode, validation


def _process_boolean(arg, default=False):
    """Process an argument to a boolean.

    Parameters
    ----------
    arg : bool
        Argument to convert.
    default : bool
        Output in case the operation fails.

    Returns
    -------
    bool
        Boolean value.
    """
    try:
        return boolean(arg)
    except TypeError:
        return default


def create_template_environment(template_parameters, src, template_encoding=None):
    """Parses boolean parameters for Jinja2 and returns a TemplateRenderer
    instance.

    Parameters
    ----------
    template_parameters : dict
        Parameters for creating the template environment.
    src : str
        Local path where the templates are located.
    template_encoding : dict, optional
        Encoding used by the templates. If not
        given, the default locale set in the system will be used.

    Returns
    -------
    TemplateRenderer
        Object with a new template environment ready to
        render the templates found in src.
    """
    if template_parameters.get("lstrip_blocks"):
        template_parameters["lstrip_blocks"] = _process_boolean(template_parameters.get("lstrip_blocks"), default=False)
    if template_parameters.get("trim_blocks"):
        template_parameters["trim_blocks"] = _process_boolean(template_parameters.get("trim_blocks"), default=True)
    if template_parameters.get("keep_trailing_newline"):
        template_parameters["keep_trailing_newline"] = _process_boolean(template_parameters.get("keep_trailing_newline"), default=False)
    if template_parameters.get("auto_reload"):
        template_parameters["auto_reload"] = _process_boolean(template_parameters.get("auto_reload"), default=False)
    if template_parameters.get("autoescape"):
        template_parameters["autoescape"] = _process_boolean(template_parameters.get("autoescape"), default=True)

    if not template_encoding:
        template_encoding = encode.Defaults.get_default_system_charset()

    return TemplateRenderer(src, template_encoding, **template_parameters)


class TemplateRenderer:
    _ALLOWED_NEWLINE_DELIMITERS = ["\n", "\r", "\r\n"]
    _FIXABLE_NEWLINE_DELIMITERS = ["\\n", "\\r", "\\r\\n"]
    _NEWLINE_DELIMITER_SWAP = {
        "\\n": "\n",
        "\\r": "\r",
        "\\r\\n": "\r\n"
    }

    def __init__(
        self,
        template_path,
        encoding,
        variable_start_string="{{",
        variable_end_string="}}",
        block_start_string="{%",
        block_end_string="%}",
        comment_start_string="{#",
        comment_end_string="#}",
        line_statement_prefix=None,
        line_comment_prefix=None,
        lstrip_blocks=False,
        trim_blocks=True,
        keep_trailing_newline=False,
        newline_sequence="\n",
        auto_reload=False,
        autoescape=True
    ):
        """This class implements functionality to load and render Jinja2
        templates. To add support for Jinja2 in a module, you need to include
        the template.py doc fragment, add the options for configuring the Jinja2
        environment to the module's options, and instantiate this class to
        render templates inside an action plugin.

        Initializes a new TemplateRenderer object with a Jinja2
        environment that can use templates from a given directory.
        More information about Jinja2 templates and environments can
        be found at https://jinja.palletsprojects.com/en/3.0.x/api/.

        Parameters
        ----------
        template_path : str
            Path to a Jinja2 template file or directory.
        encoding : str
            Encoding for rendered templates.
        variable_start_string : str, optional
            Marker for the beginning of
            a statement to print a variable in Jinja2.
        variable_end_string : str, optional
            Marker for the end of
            a statement to print a variable in Jinja2.
        block_start_string : str, optional
            Marker for the beginning of
            a block in Jinja2.
        block_end_string : str, optional
            Marker for the end of a block
            in Jinja2.
        comment_start_string : str, optional
            Marker for the beginning of
            a comment in Jinja2.
        comment_end_string : str, optional
            Marker for the end of a comment
            in Jinja2.
        line_statement_prefix : str, optional
            Prefix used by Jinja2 to identify
            line-based statements.
        line_comment_prefix : str, optional
            Prefix used by Jinja2 to identify
            comment lines.
        lstrip_blocks : bool, optional
            Whether Jinja2 should strip leading spaces
            from the start of a line to a block.
        trim_blocks : bool, optional
            Whether Jinja2 should remove the first
            newline after a block is removed.
        keep_trailing_newline : bool, optional
            Whether Jinja2 should keep the
            first trailing newline at the end of a template after rendering.
        newline_sequence : str, optional
            Sequence that starts a newline in a
            template. Valid values are '\n', '\r', '\r\n'.
        auto_reload : bool, optional
            Whether to reload a template file when it
            has changed after creating the Jinja2 environment.
        autoescape : bool, optional
            Whether to enable autoescape of XML/HTML elements.

        Attributes
        ----------
        encoding : str
            Encoding for rendered templates.
        template_dir : str
            Dir with the template path.
        templating_env : jinja2.environment
            Environment created with the arguments as input.

        Raises
        ------
        FileNotFoundError
            When template_path points to a non-existent
            file or directory.
        ValueError
            When the newline sequence is not valid.
        """
        if not path.exists(template_path):
            raise FileNotFoundError("The template path {0} does not exist".format(
                template_path
            ))

        template_canonical_path = path.realpath(template_path)
        if path.isdir(template_canonical_path):
            template_dir = template_canonical_path
        else:
            template_dir = path.dirname(template_canonical_path)

        if newline_sequence in self._FIXABLE_NEWLINE_DELIMITERS:
            newline_sequence = self._NEWLINE_DELIMITER_SWAP[newline_sequence]

        if newline_sequence not in self._ALLOWED_NEWLINE_DELIMITERS:
            raise ValueError("Newline delimiter '{0}' is not valid".format(
                to_native(newline_sequence)
            ))

        self.encoding = encoding
        self.template_dir = template_dir

        environment_args = {
            'block_start_string': block_start_string,
            'block_end_string': block_end_string,
            'variable_start_string': variable_start_string,
            'variable_end_string': variable_end_string,
            'comment_start_string': comment_start_string,
            'comment_end_string': comment_end_string,
            'line_statement_prefix': line_statement_prefix,
            'line_comment_prefix': line_comment_prefix,
            'trim_blocks': trim_blocks,
            'lstrip_blocks': lstrip_blocks,
            'newline_sequence': newline_sequence,
            'keep_trailing_newline': keep_trailing_newline,
            'loader': jinja2.FileSystemLoader(
                searchpath=template_dir,
                encoding=encoding,
            ),
            'auto_reload': auto_reload
        }

        # Setting autoescape this way so bandit understands we're following best
        # practices in regards to jinja autoescaping.
        if autoescape:
            self.templating_env = jinja2.Environment(autoescape=True, **environment_args)
        else:
            self.templating_env = jinja2.Environment(autoescape=jinja2.select_autoescape(), **environment_args)

    def _prepare_template_variables(self, variables, templar=None, display=None):
        """Prepare variables for template rendering by optionally resolving
        them using Ansible's templar.

        This method ensures that nested variables and Jinja2 expressions in
        variable values are properly resolved before template rendering.
        It also unpacks dict loop items so that flat variable names like
        ``{{ ds_name }}`` resolve without requiring ``{{ item.ds_name }}``
        in the template, mirroring the behaviour of Ansible's own template
        module.

        Parameters
        ----------
        variables : dict
            Dictionary containing all variables including task context,
            loop variables, and user-defined variables.
        templar : ansible.template.Templar, optional
            Ansible's templar instance for resolving nested variables.
            If provided, string variables will be templated before rendering.

        Returns
        -------
        dict
            Variables ready for template rendering, with loop items merged
            and nested expressions resolved if templar was provided.

        Raises
        ------
        TypeError
            If variables is not a dict type.

        Notes
        -----
        - Only string values are passed to the templar; non-string values
          (dicts, lists, booleans, integers, etc.) are carried over as-is
          since they cannot contain Jinja2 expressions and templating them
          would be unnecessarily expensive.
        - Templating failures for individual variables are handled gracefully,
          falling back to the original value.
        - Jinja2 template errors and common Python type/attribute errors are
          caught per-variable, falling back to the original value. Other
          exceptions propagate normally.
        """
        # Validate input
        if not isinstance(variables, dict):
            raise TypeError("variables must be a dict, got {0}".format(type(variables).__name__))

        # Unpack dict loop items into the top-level namespace so flat variable
        # names like {{ ds_name }} resolve without requiring {{ item.ds_name }}
        # in the template. This mirrors the behaviour of Ansible's own template
        # module.
        loop_var = variables.get("ansible_loop_var", "item")
        loop_item = variables.get(loop_var)
        if isinstance(loop_item, dict):
            variables = dict(variables)
            variables.update(loop_item)

        # Use templar to resolve nested variables if provided
        if templar:
            resolved_vars = {}
            for key, value in variables.items():
                # Only template string values; non-string types (dicts, lists,
                # booleans, integers, etc.) cannot contain Jinja2 expressions
                # and iterating over them with templar.template() is wasteful.
                if isinstance(value, str):
                    try:
                        resolved_vars[key] = templar.template(value)
                    except Exception as err:
                        # Fall back to the original value when templating fails
                        # (e.g. AnsibleUndefinedVariable, jinja2.TemplateError).
                        # Log at vvvv via the caller-supplied display instance
                        # so the user can diagnose with -vvvv.
                        if display is not None:
                            display.vvvv(
                                "ibm_zos_core template.py: could not resolve variable "
                                "'{0}' (value: {1!r}): {2}".format(key, value, to_native(err))
                            )
                        resolved_vars[key] = value
                else:
                    resolved_vars[key] = value
            return resolved_vars

        return variables

    def render_file_template(self, file_path, variables, templar=None, display=None):
        """Loads a template from the templates directory and renders
        it using the Jinja2 environment configured in the object.

        Parameters
        ----------
        file_path : str
            Relative path (from the template directory)
            to a template.
        variables : dict
            Dictionary containing the variables and
            their values that will be substituted in the template.
        templar : ansible.template.Templar, optional
            Ansible's templar instance for resolving nested variables.
            If provided, all variables will be templated before rendering
            to ensure proper variable resolution.

        Returns
        -------
        tuple(str,str)
            Filepath to a temporary directory that contains the
            rendered template, and the complete filepath to the
            rendered template.

        Raises
        ------
        TemplateNotFound
            When the template file doesn't exist in the
            template directory.
        TemplateError
            When rendering of the template fails.
        FileExistsError
            When there is an error while trying to create the
            temp directory for rendered templates.
        PermissionError
            When there is an error accessing the temp directory.
        IOError
            When there is an error writing the rendered template.
        ValueError
            When there is an error writing the rendered template.
        """
        # Prepare variables by resolving nested expressions with templar
        prepared_vars = self._prepare_template_variables(variables, templar, display)
        try:
            template = self.templating_env.get_template(file_path)
            rendered_contents = template.render(prepared_vars)
        except jinja2.TemplateNotFound as err:
            raise jinja2.TemplateNotFound("Template {0} was not found: {1}".format(
                file_path,
                to_native(err)
            ))
        except jinja2.TemplateError as err:
            raise jinja2.TemplateError("Error while rendering {0}: {1}".format(
                file_path,
                to_native(err)
            ))

        try:
            temp_template_dir = tempfile.mkdtemp()
        except FileExistsError as err:
            raise FileExistsError("Unable to create directory for rendered templates: {0}".format(
                to_native(err)
            ))
        except PermissionError as err:
            raise PermissionError("Error while trying to access temporary directory for templates: {0}".format(
                to_native(err)
            ))

        try:
            template_file_path = path.join(validation.validate_safe_path(temp_template_dir), validation.validate_safe_path(file_path))
            with open(template_file_path, mode="w", encoding=self.encoding) as template:
                template.write(rendered_contents)
        # There could be encoding errors.
        except IOError as err:
            raise IOError("An error ocurred while writing the rendered template for {0}: {1}".format(
                file_path,
                to_native(err)
            ))
        except ValueError as err:
            raise ValueError("An error ocurred while writing the rendered template for {0}: {1}".format(
                file_path,
                to_native(err)
            ))

        return temp_template_dir, template_file_path

    def render_dir_template(self, variables, templar=None, display=None):
        """Loads all templates from a directory and renders
        them using the Jinja2 environment configured in the object.

        Parameters
        ----------
        variables : dict
            Dictionary containing the variables and
            their values that will be substituted in the template.
        templar : ansible.template.Templar, optional
            Ansible's templar instance for resolving nested variables.
            If provided, all variables will be templated before rendering
            to ensure proper variable resolution.

        Returns
        -------
        tuple(str,str)
            Filepath to a temporary directory that contains the
            rendered templates, and the complete filepath to the
            rendered templates' directory.

        Raises
        ------
        TemplateNotFound
            When the template file doesn't exist in the
            template directory.
        TemplateError
            When rendering of the template fails.
        FileExistsError
            When there is an error while trying to create the
            temp directory for rendered templates.
        PermissionError
            When there is an error accessing the temp directory.
        OSError
            When there is an error while trying to create the
            temp directory for rendered templates.
        IOError
            When there is an error writing the rendered template.
        ValueError
            When there is an error writing the rendered template.
        """
        # Prepare variables by resolving nested expressions with templar
        prepared_vars = self._prepare_template_variables(variables, templar, display)
        try:
            temp_parent_dir = tempfile.mkdtemp()
            last_dir = os.path.basename(self.template_dir)
            temp_template_dir = os.path.join(validation.validate_safe_path(temp_parent_dir), validation.validate_safe_path(last_dir))
            os.makedirs(temp_template_dir, exist_ok=True)
        except FileExistsError as err:
            raise FileExistsError("Unable to create directory for rendered templates: {0}".format(
                to_native(err)
            ))
        except PermissionError as err:
            raise PermissionError("Error while trying to access temporary directory: {0}".format(
                to_native(err)
            ))
        except OSError as err:
            raise OSError("Error while trying to access temporary directory: {0}".format(
                to_native(err)
            ))

        for dirpath, subdirs, files in os.walk(self.template_dir):
            for template_file in files:
                relative_dir = os.path.relpath(
                    validation.validate_safe_path(dirpath),
                    validation.validate_safe_path(self.template_dir)
                )
                file_path = os.path.normpath(
                    os.path.join(
                        validation.validate_safe_path(relative_dir),
                        validation.validate_safe_path(template_file)
                    )
                )
                try:
                    template = self.templating_env.get_template(file_path)
                    rendered_contents = template.render(prepared_vars)
                except jinja2.TemplateNotFound as err:
                    raise jinja2.TemplateNotFound("Template {0} was not found: {1}".format(
                        file_path,
                        to_native(err)
                    ))
                except jinja2.TemplateError as err:
                    raise jinja2.TemplateError("Error while rendering {0}: {1}".format(
                        file_path,
                        to_native(err)
                    ))

                try:
                    template_file_path = os.path.join(
                        validation.validate_safe_path(temp_template_dir),
                        validation.validate_safe_path(file_path)
                    )
                    os.makedirs(os.path.dirname(template_file_path), exist_ok=True)
                    with open(template_file_path, mode="w", encoding=self.encoding) as temp:
                        temp.write(rendered_contents)
                except IOError as err:
                    raise IOError("An error ocurred while writing the rendered template for {0}: {1}".format(
                        file_path,
                        to_native(err)
                    ))
                except ValueError as err:
                    raise ValueError("An error ocurred while writing the rendered template for {0}: {1}".format(
                        file_path,
                        to_native(err)
                    ))

        return temp_parent_dir, temp_template_dir
