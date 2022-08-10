#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2021 dailyinnovation.biz
"""
import logging
import logging.handlers
import time
import sys
import os
import plistlib
import json

__author__ = "Mush Mo <mush@dailyinnovation.biz>"


UNSET = object()
ICON_ROOT = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources'

ICON_ACCOUNT = os.path.join(ICON_ROOT, 'Accounts.icns')
ICON_BURN = os.path.join(ICON_ROOT, 'BurningIcon.icns')
ICON_CLOCK = os.path.join(ICON_ROOT, 'Clock.icns')
ICON_COLOR = os.path.join(ICON_ROOT, 'ProfileBackgroundColor.icns')
ICON_COLOUR = ICON_COLOR  # Queen's English, if you please
ICON_EJECT = os.path.join(ICON_ROOT, 'EjectMediaIcon.icns')
# Shown when a workflow throws an error
ICON_ERROR = os.path.join(ICON_ROOT, 'AlertStopIcon.icns')
ICON_FAVORITE = os.path.join(ICON_ROOT, 'ToolbarFavoritesIcon.icns')
ICON_FAVOURITE = ICON_FAVORITE
ICON_GROUP = os.path.join(ICON_ROOT, 'GroupIcon.icns')
ICON_HELP = os.path.join(ICON_ROOT, 'HelpIcon.icns')
ICON_HOME = os.path.join(ICON_ROOT, 'HomeFolderIcon.icns')
ICON_INFO = os.path.join(ICON_ROOT, 'ToolbarInfo.icns')
ICON_NETWORK = os.path.join(ICON_ROOT, 'GenericNetworkIcon.icns')
ICON_NOTE = os.path.join(ICON_ROOT, 'AlertNoteIcon.icns')
ICON_SETTINGS = os.path.join(ICON_ROOT, 'ToolbarAdvanced.icns')
ICON_SWIRL = os.path.join(ICON_ROOT, 'ErasingIcon.icns')
ICON_SWITCH = os.path.join(ICON_ROOT, 'General.icns')
ICON_SYNC = os.path.join(ICON_ROOT, 'Sync.icns')
ICON_TRASH = os.path.join(ICON_ROOT, 'TrashIcon.icns')
ICON_USER = os.path.join(ICON_ROOT, 'UserIcon.icns')
ICON_WARNING = os.path.join(ICON_ROOT, 'AlertCautionIcon.icns')
ICON_WEB = os.path.join(ICON_ROOT, 'BookmarkIcon.icns')

class Variables(dict):

    def __init__(self, arg=None, **variables):
        """Create a new `Variables` object."""
        self.arg = arg
        self.config = {}
        super(Variables, self).__init__(**variables)

    @property
    def obj(self):
        """``alfredworkflow`` :class:`dict`."""
        o = {}
        if self:
            d2 = {}
            for k, v in self.items():
                d2[k] = v
            o['variables'] = d2

        if self.config:
            o['config'] = self.config

        if self.arg is not None:
            o['arg'] = self.arg

        return {'alfredworkflow': o}


class Modifier(object):

    def __init__(self, key, subtitle=None, arg=None, valid=None, icon=None,
                 icontype=None):
        """Create a new :class:`Modifier`.

        Don't use this class directly (as it won't be associated with any
        :class:`Item3`), but rather use :meth:`Item3.add_modifier()`
        to add modifiers to results.

        Args:
            key (unicode): Modifier key, e.g. ``"cmd"``, ``"alt"`` etc.
            subtitle (unicode, optional): Override default subtitle.
            arg (unicode, optional): Argument to pass for this modifier.
            valid (bool, optional): Override item's validity.
            icon (unicode, optional): Filepath/UTI of icon to use
            icontype (unicode, optional): Type of icon. See
                :meth:`Workflow.add_item() <workflow.Workflow.add_item>`
                for valid values.

        """
        self.key = key
        self.subtitle = subtitle
        self.arg = arg
        self.valid = valid
        self.icon = icon
        self.icontype = icontype

        self.config = {}
        self.variables = {}

    def setvar(self, name, value):
        """Set a workflow variable for this Item.

        Args:
            name (unicode): Name of variable.
            value (unicode): Value of variable.

        """
        self.variables[name] = value

    def getvar(self, name, default=None):
        """Return value of workflow variable for ``name`` or ``default``.

        Args:
            name (unicode): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            unicode or ``default``: Value of variable if set or ``default``.

        """
        return self.variables.get(name, default)

    @property
    def obj(self):
        """Modifier formatted for JSON serialization for Alfred 3.

        Returns:
            dict: Modifier for serializing to JSON.

        """
        o = {}

        if self.subtitle is not None:
            o['subtitle'] = self.subtitle

        if self.arg is not None:
            o['arg'] = self.arg

        if self.valid is not None:
            o['valid'] = self.valid

        if self.variables:
            o['variables'] = self.variables

        if self.config:
            o['config'] = self.config

        icon = self._icon()
        if icon:
            o['icon'] = icon

        return o

    def _icon(self):
        """Return `icon` object for item.

        Returns:
            dict: Mapping for item `icon` (may be empty).

        """
        icon = {}
        if self.icon is not None:
            icon['path'] = self.icon

        if self.icontype is not None:
            icon['type'] = self.icontype

        return icon


class Item5(object):
    """Represents a feedback item for Alfred 3+.

    Generates Alfred-compliant JSON for a single item.

    Don't use this class directly (as it then won't be associated with
    any :class:`Workflow3 <workflow.Workflow3>` object), but rather use
    :meth:`Workflow3.add_item() <workflow.Workflow3.add_item>`.
    See :meth:`~workflow.Workflow3.add_item` for details of arguments.

    """

    def __init__(self, title, subtitle='', arg=None, autocomplete=None,
                 match=None, valid=False, uid=None, icon=None, icontype=None,
                 type=None, largetext=None, copytext=None, quicklookurl=None):
        """Create a new :class:`Item3` object.

        Use same arguments as for
        :class:`Workflow.Item <workflow.Workflow.Item>`.

        Argument ``subtitle_modifiers`` is not supported.

        """
        self.title = title
        self.subtitle = subtitle
        self.arg = arg
        self.autocomplete = autocomplete
        self.match = match
        self.valid = valid
        self.uid = uid
        self.icon = icon
        self.icontype = icontype
        self.type = type
        self.quicklookurl = quicklookurl
        self.largetext = largetext
        self.copytext = copytext

        self.modifiers = {}

        self.config = {}
        self.variables = {}

    def setvar(self, name, value):
        """Set a workflow variable for this Item.

        Args:
            name (unicode): Name of variable.
            value (unicode): Value of variable.

        """
        self.variables[name] = value

    def getvar(self, name, default=None):
        """Return value of workflow variable for ``name`` or ``default``.

        Args:
            name (unicode): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            unicode or ``default``: Value of variable if set or ``default``.

        """
        return self.variables.get(name, default)

    def add_modifier(self, key, subtitle=None, arg=None, valid=None, icon=None,
                     icontype=None):
        """Add alternative values for a modifier key.

        Args:
            key (unicode): Modifier key, e.g. ``"cmd"`` or ``"alt"``
            subtitle (unicode, optional): Override item subtitle.
            arg (unicode, optional): Input for following action.
            valid (bool, optional): Override item validity.
            icon (unicode, optional): Filepath/UTI of icon.
            icontype (unicode, optional): Type of icon.  See
                :meth:`Workflow.add_item() <workflow.Workflow.add_item>`
                for valid values.

        In Alfred 4.1+ and Alfred-Workflow 1.40+, ``arg`` may also be a
        :class:`list` or :class:`tuple`.

        Returns:
            Modifier: Configured :class:`Modifier`.

        """
        mod = Modifier(key, subtitle, arg, valid, icon, icontype)

        # Add Item variables to Modifier
        mod.variables.update(self.variables)

        self.modifiers[key] = mod

        return mod

    @property
    def obj(self):
        """Item formatted for JSON serialization.

        Returns:
            dict: Data suitable for Alfred 3 feedback.

        """
        # Required values
        o = {
            'title': self.title,
            'subtitle': self.subtitle,
            'valid': self.valid,
        }

        # Optional values
        if self.arg is not None:
            o['arg'] = self.arg

        if self.autocomplete is not None:
            o['autocomplete'] = self.autocomplete

        if self.match is not None:
            o['match'] = self.match

        if self.uid is not None:
            o['uid'] = self.uid

        if self.type is not None:
            o['type'] = self.type

        if self.quicklookurl is not None:
            o['quicklookurl'] = self.quicklookurl

        if self.variables:
            o['variables'] = self.variables

        if self.config:
            o['config'] = self.config

        # Largetype and copytext
        text = self._text()
        if text:
            o['text'] = text

        icon = self._icon()
        if icon:
            o['icon'] = icon

        # Modifiers
        mods = self._modifiers()
        if mods:
            o['mods'] = mods

        return o

    def _icon(self):
        """Return `icon` object for item.

        Returns:
            dict: Mapping for item `icon` (may be empty).

        """
        icon = {}
        if self.icon is not None:
            icon['path'] = self.icon

        if self.icontype is not None:
            icon['type'] = self.icontype

        return icon

    def _text(self):
        """Return `largetext` and `copytext` object for item.

        Returns:
            dict: `text` mapping (may be empty)

        """
        text = {}
        if self.largetext is not None:
            text['largetype'] = self.largetext

        if self.copytext is not None:
            text['copy'] = self.copytext

        return text

    def _modifiers(self):
        """Build `mods` dictionary for JSON feedback.

        Returns:
            dict: Modifier mapping or `None`.

        """
        if self.modifiers:
            mods = {}
            for k, mod in self.modifiers.items():
                mods[k] = mod.obj

            return mods

        return None


class Workflow5Mixin(object):

    @property
    def cachedir(self):
        """Path to workflow's cache directory.

        The cache directory is a subdirectory of Alfred's own cache directory
        in ``~/Library/Caches``. The full path is in Alfred 4+ is:

        ``~/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/<bundle id>``

        For earlier versions:

        ``~/Library/Caches/com.runningwithcrayons.Alfred-X/Workflow Data/<bundle id>``

        where ``Alfred-X`` may be ``Alfred-2`` or ``Alfred-3``.

        Returns:
            unicode: full path to workflow's cache directory

        """
        if self.alfred_env.get('workflow_cache'):
            dirpath = self.alfred_env.get('workflow_cache')

        else:
            dirpath = self._default_cachedir

        return self._create(dirpath)


    @property
    def _default_cachedir(self):
        """Alfred 2's default cache directory."""
        return os.path.join(
            os.path.expanduser(
                '~/Library/Caches/com.runningwithcrayons.Alfred-2/'
                'Workflow Data/'),
            self.bundleid)

    @property
    def debugging(self):
        """Whether Alfred's debugger is open.

        :returns: ``True`` if Alfred's debugger is open.
        :rtype: ``bool``

        """
        return self.alfred_env.get('debug') == 1

    @property
    def alfred_env(self):
        """Dict of Alfred's environmental variables minus ``alfred_`` prefix.

        .. versionadded:: 1.7

        The variables Alfred 2.4+ exports are:

        ============================  =========================================
        Variable                      Description
        ============================  =========================================
        debug                         Set to ``1`` if Alfred's debugger is
                                      open, otherwise unset.
        preferences                   Path to Alfred.alfredpreferences
                                      (where your workflows and settings are
                                      stored).
        preferences_localhash         Machine-specific preferences are stored
                                      in ``Alfred.alfredpreferences/preferences/local/<hash>``
                                      (see ``preferences`` above for
                                      the path to ``Alfred.alfredpreferences``)
        theme                         ID of selected theme
        theme_background              Background colour of selected theme in
                                      format ``rgba(r,g,b,a)``
        theme_subtext                 Show result subtext.
                                      ``0`` = Always,
                                      ``1`` = Alternative actions only,
                                      ``2`` = Selected result only,
                                      ``3`` = Never
        version                       Alfred version number, e.g. ``'2.4'``
        version_build                 Alfred build number, e.g. ``277``
        workflow_bundleid             Bundle ID, e.g.
                                      ``net.deanishe.alfred-mailto``
        workflow_cache                Path to workflow's cache directory
        workflow_data                 Path to workflow's data directory
        workflow_name                 Name of current workflow
        workflow_uid                  UID of workflow
        workflow_version              The version number specified in the
                                      workflow configuration sheet/info.plist
        ============================  =========================================

        **Note:** all values are Unicode strings except ``version_build`` and
        ``theme_subtext``, which are integers.

        :returns: ``dict`` of Alfred's environmental variables without the
            ``alfred_`` prefix, e.g. ``preferences``, ``workflow_data``.

        """
        if self._alfred_env is not None:
            return self._alfred_env

        data = {}

        for key in (
                'debug',
                'preferences',
                'preferences_localhash',
                'theme',
                'theme_background',
                'theme_subtext',
                'version',
                'version_build',
                'workflow_bundleid',
                'workflow_cache',
                'workflow_data',
                'workflow_name',
                'workflow_uid',
                'workflow_version'):

            value = os.getenv('alfred_' + key, '')

            if value:
                if key in ('debug', 'version_build', 'theme_subtext'):
                    value = int(value)
                else:
                    # TODO
                    pass
                    # value = self.decode(value)

            data[key] = value

        self._alfred_env = data

        return self._alfred_env

    @property
    def version(self):
        """Return the version of the workflow.

        .. versionadded:: 1.9.10

        Get the workflow version from environment variable,
        the ``update_settings`` dict passed on
        instantiation, the ``version`` file located in the workflow's
        root directory or ``info.plist``. Return ``None`` if none
        exists or :class:`ValueError` if the version number is invalid
        (i.e. not semantic).

        :returns: Version of the workflow (not Alfred-Workflow)
        :rtype: :class:`~workflow.update.Version` object

        """
        if self._version is UNSET:

            version = None
            # environment variable has priority
            if self.alfred_env.get('workflow_version'):
                version = self.alfred_env['workflow_version']

            # Try `update_settings`
            elif self._update_settings:
                version = self._update_settings.get('version')

            # `version` file
            if not version:
                filepath = self.workflowfile('version')

                if os.path.exists(filepath):
                    with open(filepath, 'rb') as fileobj:
                        version = fileobj.read()

            # info.plist
            if not version:
                version = self.info.get('version')

            if version:
                from update import Version
                version = Version(version)

            self._version = version

        return self._version

    @property
    def logger(self):
        """Logger that logs to both console and a log file.

        If Alfred's debugger is open, log level will be ``DEBUG``,
        else it will be ``INFO``.

        Use :meth:`open_log` to open the log file in Console.

        :returns: an initialised :class:`~logging.Logger`

        """
        if self._logger:
            return self._logger

        # Initialise new logger and optionally handlers
        logger = logging.getLogger('')

        # Only add one set of handlers
        # Exclude from coverage, as pytest will have configured the
        # root logger already
        if not len(logger.handlers):  # pragma: no cover

            fmt = logging.Formatter(
                '%(asctime)s %(filename)s:%(lineno)s'
                ' %(levelname)-8s %(message)s',
                datefmt='%H:%M:%S')

            logfile = logging.handlers.RotatingFileHandler(
                self.logfile,
                maxBytes=1024 * 1024,
                backupCount=1)
            logfile.setFormatter(fmt)
            logger.addHandler(logfile)

            console = logging.StreamHandler()
            console.setFormatter(fmt)
            logger.addHandler(console)

        if self.debugging:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        self._logger = logger

        return self._logger

    @property
    def logfile(self):
        """Path to logfile.

        :returns: path to logfile within workflow's cache directory
        :rtype: ``unicode``

        """
        return self.cachefile('%s.log' % self.bundleid)

    @property
    def bundleid(self):
        """Workflow bundle ID from environmental vars or ``info.plist``.

        :returns: bundle ID
        :rtype: ``unicode``

        """
        if not self._bundleid:
            if self.alfred_env.get('workflow_bundleid'):
                self._bundleid = self.alfred_env.get('workflow_bundleid')
            else:
                self._bundleid = self.info['bundleid']

        return self._bundleid

    @property
    def name(self):
        """Workflow name from Alfred's environmental vars or ``info.plist``.

        :returns: workflow name
        :rtype: ``unicode``

        """
        if not self._name:
            if self.alfred_env.get('workflow_name'):
                self._name = self.alfred_env.get('workflow_name')
            else:
                self._name = self.info['name']

        return self._name

    @property
    def info(self):
        """:class:`dict` of ``info.plist`` contents."""
        if not self._info_loaded:
            self._load_info_plist()
        return self._info

    @property
    def workflowdir(self):
        """Path to workflow's root directory (where ``info.plist`` is).

        Returns:
            unicode: full path to workflow root directory

        """
        if not self._workflowdir:
            # Try the working directory first, then the directory
            # the library is in. CWD will be the workflow root if
            # a workflow is being run in Alfred
            candidates = [
                os.path.abspath(os.getcwd()),
                os.path.dirname(os.path.abspath(os.path.dirname(__file__)))]

            # climb the directory tree until we find `info.plist`
            for dirpath in candidates:

                # Ensure directory path is Unicode
                # TODO removed without test
                # dirpath = self.decode(dirpath)

                while True:
                    if os.path.exists(os.path.join(dirpath, 'info.plist')):
                        self._workflowdir = dirpath
                        break

                    elif dirpath == '/':
                        # no `info.plist` found
                        break

                    # Check the parent directory
                    dirpath = os.path.dirname(dirpath)

                # No need to check other candidates
                if self._workflowdir:
                    break

            if not self._workflowdir:
                raise IOError("'info.plist' not found in directory tree")

        return self._workflowdir

    @property
    def store_data_path(self):
        return os.path.join(self.cachedir, 'store_data.json')


class Workflow5(Workflow5Mixin):

    def __init__(self, update_settings=None):
        self._logger = None
        self._alfred_env = None
        # Version number of the workflow
        self._version = UNSET
        # Version from last workflow run
        self._last_version_run = UNSET
        self._bundleid = None
        self._info_loaded = False
        self._workflowdir = None
        self.help_url = None
        self._name = None
        self._rerun = 0
        self._update_settings = update_settings or {}
        self._items = []
        self.variables = {}
        self._session_id = os.getenv('_WF_SESSION_ID') or None
        if self._session_id:
            self.set_var('_WF_SESSION_ID', self._session_id)
        self._is_firstrun = os.getenv('_WF_FIRSTRUN', 'true')

    @property
    def session_id(self):
        if not self._session_id:
            from uuid import uuid4
            self._session_id = uuid4().hex
            self.set_var('_WF_SESSION_ID', self._session_id)

        return self._session_id

    @property
    def is_firstrun(self):
        self.set_var('_WF_FIRSTRUN', "false")
        return self._is_firstrun == 'true'

    def run(self, func, text_errors=False):
        """Call ``func`` to run your workflow.

        :param func: Callable to call with ``self`` (i.e. the :class:`Workflow`
            instance) as first argument.
        :param text_errors: Emit error messages in plain text, not in
            Alfred's XML/JSON feedback format. Use this when you're not
            running Alfred-Workflow in a Script Filter and would like
            to pass the error message to, say, a notification.
        :type text_errors: ``Boolean``

        ``func`` will be called with :class:`Workflow` instance as first
        argument.

        ``func`` should be the main entry point to your workflow.

        Any exceptions raised will be logged and an error message will be
        output to Alfred.

        """
        start = time.time()

        # Write to debugger to ensure "real" output starts on a new line
        print('.', file=sys.stderr)

        # Call workflow's entry function/method within a try-except block
        # to catch any errors and display an error message in Alfred
        try:
            if self.version:
                self.logger.debug('---------- %s (%s) ----------',
                                  self.name, self.version)
            else:
                self.logger.debug('---------- %s ----------', self.name)

            # Run update check if configured for self-updates.
            # This call has to go in the `run` try-except block, as it will
            # initialise `self.settings`, which will raise an exception
            # if `settings.json` isn't valid.
            if self._update_settings:
                self.check_update()

            # Run workflow's entry function/method
            func(self)

            # Set last version run to current version after a successful
            # run
            self.set_last_version()

        except Exception as err:
            self.logger.exception(err)
            if self.help_url:
                self.logger.info('for assistance, see: %s', self.help_url)

            if not sys.stdout.isatty():  # Show error in Alfred
                if text_errors:
                    print(err.encode('utf-8'), end='')
                else:
                    self._items = []
                    if self._name:
                        name = self._name
                    elif self._bundleid:  # pragma: no cover
                        name = self._bundleid
                    else:  # pragma: no cover
                        name = os.path.dirname(__file__)
                    # TODO show error
                    self.logger.debug(err)
                    self.add_item("Error in workflow '%s'" % name,
                                  err,
                                  icon=ICON_ERROR)
                    self.send_feedback()
            return 1

        finally:
            self.logger.debug('---------- finished in %0.3fs ----------',
                              time.time() - start)

        return 0


    def _load_info_plist(self):
        """Load workflow info from ``info.plist``."""
        # info.plist should be in the directory above this one
        self._info = plistlib.load(open(self.workflowfile('info.plist'), 'rb'), fmt=plistlib.FMT_XML)
        self._info_loaded = True

    def workflowfile(self, filename):
        """Return full path to ``filename`` in workflow's root directory.

        :param filename: basename of file
        :type filename: ``unicode``
        :returns: full path to file within data directory
        :rtype: ``unicode``

        """
        return os.path.join(self.workflowdir, filename)

    def cachefile(self, filename):
        """Path to ``filename`` in workflow's cache directory.

        Return absolute path to ``filename`` within your workflow's
        :attr:`cache directory <Workflow.cachedir>`.

        :param filename: basename of file
        :type filename: ``unicode``
        :returns: full path to file within cache directory
        :rtype: ``unicode``

        """
        return os.path.join(self.cachedir, filename)

    def _create(self, dirpath):
        """Create directory `dirpath` if it doesn't exist.

        :param dirpath: path to directory
        :type dirpath: ``unicode``
        :returns: ``dirpath`` argument
        :rtype: ``unicode``

        """
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        return dirpath

    def set_last_version(self, version=None):
        """Set :attr:`last_version_run` to current version.

        .. versionadded:: 1.9.10

        :param version: version to store (default is current version)
        :type version: :class:`~workflow.update.Version` instance
            or ``unicode``
        :returns: ``True`` if version is saved, else ``False``

        """
        # TODO, 未实现
        # if not version:
        #     if not self.version:
        #         self.logger.warning(
        #             "Can't save last version: workflow has no version")
        #         return False

        #     version = self.version

        # if isinstance(version, basestring):
        #     from update import Version
        #     version = Version(version)

        # self.settings['__workflow_last_version'] = str(version)

        # self.logger.debug('set last run version: %s', version)

        return True

    def store_data(self, name, value):
        data = {}
        try:
            with open(self.store_data_path) as f_data:
                data = json.load(f_data)
        except FileNotFoundError:
            self.logger.warning("Can not load stored data, file not found")
        except json.JSONDecodeError as e:
            self.logger.warning(f"Decode failed, error: {e}")
        data.update({name: value})
        with open(self.store_data_path, 'w') as f_data:
            json.dump(data, f_data)

    def stored_data(self, name, default=None):
        try:
            with open(self.store_data_path) as f_data:
                data = json.load(f_data)
                return data.get(name, default)
        except FileNotFoundError:
            self.logger.warning("Can not load stored data, file not found")
        except json.JSONDecodeError as e:
            self.logger.warning(f"Decode failed, error: {e}")

    @property
    def rerun(self):
        """How often (in seconds) Alfred should re-run the Script Filter."""
        return self._rerun

    @rerun.setter
    def rerun(self, seconds):
        """Interval at which Alfred should re-run the Script Filter.

        Args:
            seconds (int): Interval between runs.
        """
        self._rerun = seconds

    def add_item(
        self,
        title,
        subtitle='',
        arg=None,
        autocomplete=None,
        valid=False,
        uid=None,
        icon=None,
        icontype=None,
        type=None,
        largetext=None,
        copytext=None,
        quicklookurl=None,
        match=None
    ):
        """Add an item to be output to Alfred.

        Args:
            match (unicode, optional): If you have "Alfred filters results"
                turned on for your Script Filter, Alfred (version 3.5 and
                above) will filter against this field, not ``title``.

        In Alfred 4.1+ and Alfred-Workflow 1.40+, ``arg`` may also be a
        :class:`list` or :class:`tuple`.

        See :meth:`Workflow.add_item() <workflow.Workflow.add_item>` for
        the main documentation and other parameters.

        The key difference is that this method does not support the
        ``modifier_subtitles`` argument. Use the :meth:`~Item3.add_modifier()`
        method instead on the returned item instead.

        Returns:
            Item3: Alfred feedback item.

        """
        item = Item5(
            title,
            subtitle,
            arg,
            autocomplete,
            match,
            valid,
            uid,
            icon,
            icontype,
            type,
            largetext,
            copytext,
            quicklookurl
        )

        # Add variables to child item
        # TODO
        # item.variables.update(self.variables)

        self._items.append(item)
        return item

    @property
    def feedback(self):
        data = {
            "variables": self.variables,
            "items": [item.obj for item in self._items]
        }
        if self.rerun:
            data['rerun'] = self.rerun
        return json.dumps(data)

    def send_feedback(self):
        _feedback = self.feedback
        if self.debugging:
            self.logger.debug(_feedback)
        sys.stdout.write(_feedback)
        sys.stdout.flush()

    def set_var(self, name, value):
        self.variables[name] = value

    def get_var(self, name, default=None):
        value = self.variables.get(name, default)
        return os.getenv(name, value)
