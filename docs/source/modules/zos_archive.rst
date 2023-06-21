
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_archive.py

.. _zos_archive_module:


zos_archive -- Archive a dataset on z/OS.
=========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Creates or extends an archive.
- The source and archive are on the remote host, and the archive is not copied to the local host.






Parameters
----------


path
  Remote absolute path, glob, or list of paths or globs for the file or files to compress or archive.

  | **required**: True
  | **type**: list
  | **elements**: str


format
  The type of compression to use.

  | **required**: False
  | **type**: dict


  name
    The name of the format to use.

    | **required**: False
    | **type**: str
    | **default**: gz
    | **choices**: bz2, gz, tar, zip, terse, xmit, pax


  format_options
    Options specific to each format.

    | **required**: False
    | **type**: dict


    terse_pack
      Pack option to use for terse format.

      | **required**: False
      | **type**: str
      | **choices**: PACK, SPACK


    xmit_log_dataset
      Provide a name of data set to use for xmit log.

      | **required**: False
      | **type**: str


    use_adrdssu
      If set to true, after unpacking a data set in ``xmit`` or ``terse`` format it will perform a single DFSMSdss ADRDSSU DUMP step.

      | **required**: False
      | **type**: bool




dest
  The file name of the dest archive.

  | **required**: False
  | **type**: str


exclude_path
  Remote absolute path, glob, or list of paths, globs or data set name patterns for the file, files or data sets to exclude from path list and glob expansion.

  | **required**: False
  | **type**: list
  | **elements**: str


group
  Name of the group that should own the filesystem object, as would be fed to chown.

  When left unspecified, it uses the current group of the current user unless you are root, in which case it can preserve the previous ownership.

  | **required**: False
  | **type**: str


mode
  The permissions the resulting filesystem object should have.

  | **required**: False
  | **type**: str


owner
  Name of the user that should own the filesystem object, as would be fed to chown.

  When left unspecified, it uses the current user unless you are root, in which case it can preserve the previous ownership.

  | **required**: False
  | **type**: str


exclusion_patterns
  Glob style patterns to exclude files or directories from the resulting archive.

  This differs from *exclude_path* which applies only to the source paths from *path*.

  | **required**: False
  | **type**: list
  | **elements**: str


remove
  Remove any added source files and trees after adding to archive.

  | **required**: False
  | **type**: bool


tmp_hlq
  High Level Qualifier used for temporary datasets.

  | **required**: False
  | **type**: str


force
  Create the dest archive file even if it already exists.

  | **required**: False
  | **type**: bool




Examples
--------

.. code-block:: yaml+jinja

   
   # Simple archive
   - name: Archive file into tar
       zos_archive:
         path: /tmp/archive/foo.txt
         dest: /tmp/archive/foo_archive_test.tar
         format:
           name: tar

   # Archive multiple files
   - name: Compress list of files into zip
       zos_archive:
         path: 
         - /tmp/archive/foo.txt
         - /tmp/archive/bar.txt
         dest: /tmp/archive/foo_bar_archive_test.zip
         format:
           name: zip

   # Archive one data set into terse
   - name: Compress data set into terse
       zos_archive:
         path: "USER.ARCHIVE.TEST"
         dest: "USER.ARCHIVE.RESULT.TRS"
         format:
           name: terse

   # Usae terse with different options
   - name: Compress data set into terse, specify pack algorithm and use adrdssu
       zos_archive:
         path: "USER.ARCHIVE.TEST"
         dest: "USER.ARCHIVE.RESULT.TRS"
         format:
           name: terse
           format_options:
             terse_pack: "SPACK"
             use_adrdssu: True

   # Use a pattern to store
   - name: Compress data set pattern using xmit
       zos_archive:
         path: "USER.ARCHIVE.*"
         exclude_paths: "USER.ARCHIVE.EXCLUDE.*"
         dest: "USER.ARCHIVE.RESULT.XMIT"
         format:
           name: xmit










Return Values
-------------


state
  The state of the input ``path``.

  | **returned**: always
  | **type**: str

dest_state
  The state of the *dest* file.

  ``absent`` when the file does not exist.

  ``archive`` when the file is an archive.

  ``compress`` when the file is compressed, but not an archive.

  ``incomplete`` when the file is an archive, but some files under *path* were not found.

  | **returned**: success
  | **type**: str

missing
  Any files that were missing from the source.

  | **returned**: success
  | **type**: list

archived
  Any files that were compressed or added to the archive.

  | **returned**: success
  | **type**: list

arcroot
  The archive root.

  | **returned**: always
  | **type**: str

expanded_paths
  The list of matching paths from paths argument.

  | **returned**: always
  | **type**: list

expanded_exclude_paths
  The list of matching exclude paths from the exclude_path argument.

  | **returned**: always
  | **type**: list

