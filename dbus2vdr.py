#!/usr/bin/python3
import dbus

class DBus2VDR:
    def __init__(self, bus, instance=0, modules=["all"]):
        self.bus = bus
        self.instance = instance
        if "all" in modules:
            self.modules = ["Recordings", "Channels", "EPG", "Plugins", "Remote",
                        "Setup", "Shutdown", "Skin", "Timers", "vdr"
            ]
        else:
            self.modules = modules
        self.init_modules()

    def init_modules(self):
        for module in self.modules:
            exec("%s(self.bus)" % module)
            setattr(self, module, eval(module+"(self.bus, self.instance)"))
            print("init %s" % module)

    def checkVDRstatus(self):
        try:
            if self.vdr:
                pass
        except AttributeError:
            self.modules.append('vdr')
            self.init_modules()
        message = self.vdr.Status()
        if message == "Ready":
            return True
        else:
            return False


class DBusClass:
    def __init__(self, bus, obj, interface, instance=0):
        self.bus = bus
        self.vdr_addr = "de.tvdr.vdr"
        self.interface = "{0}.{1}".format(self.vdr_addr, interface)
        if instance > 0:
            self.dbus = self.bus.get_object("{0}{1}".format(self.vdr_addr, instance),
                                            obj)
        else:
            self.dbus = self.bus.get_object(self.vdr_addr, obj)


class Channels(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Channels", "channel",
                         instance)

    def Count(self):
        """get count of channels"""
        return self.dbus.Count(dbus_interface=self.interface)

    def GetFromTo(self, from_index, to_index):
        """get channels between from_index and to_index"""
        return self.dbus.GetFromTo(dbus.Int32(from_index), dbus.Int32(to_index),
                                   dbus_interface=self.interface)

    def List(self, filter):
        """filter may contain on of groups|<number>|<name>|<id>"""
        return self.dbus.List(dbus.String(filter), dbus_interface=self.interface)


class EPG(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/EPG", 'epg')

    def DisableEitScanner(self, timeout=0):
        """disable EIT scanner with timeout (default: 3600)"""
        return self.dbus.DisableEitScanner(dbus.Int32(timeout),
                                               dbus_interface=self.interface)

    def EnableEitScanner(self):
        """enable EIT scanner"""
        return self.dbus.EnableEitScanner(dbus_interface=self.interface)

    def ClearEpg(self, timeout=0):
        """clear EPG data with a value for inactivity timeout of eit-scanner (default: 10)"""
        return self.dbus.ClearEpg(dbus.Int32(timeout),
                                  dbus_interface=self.interface)

    def PutEntry(self, array=[]):
        """add EPG entry from list ["C ...", "E ...", "..."]"""
        return self.dbus.PutEntry(dbus.Array(array, "s"),
                                  dbus_interface=self.interface)

    def PutFile(self, path=""):
        """read EPG data from file"""
        return self.dbus.PutFile(dbus.String(path),
                                 dbus_interface=self.interface)

    def Now(self, channel=""):
        """get current event of given or all channels if string is empty"""
        return self.dbus.Now(dbus.String(channel),
                             dbus_interface=self.interface)

    def Next(self, channel=""):
        """get next event of given or all channels if string is empty"""
        return self.dbus.Next(dbus.String(channel),
                             dbus_interface=self.interface)

    def At(self, channel="", time=0):
        """get next event of given or all channels if string is empty"""
        return self.dbus.At(dbus.String(channel), dbus.UInt64(time),
                             dbus_interface=self.interface)


class Plugins(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Plugins", 'plugin')

    def SVDRPCommand(self, plugin="", command="", args=""):
        """send SVDRP commands to plugins"""
        tdbus = self.bus.get_object("de.tvdr.vdr","/Plugins/%s" % plugin)
        return tdbus.SVDRPCommand(dbus.String(command), dbus.String(args),
                            dbus_interface=self.interface)

    def Service(self, id, data):
        """call Service method of plugins"""
        return self.dbus.Service(dbus.String(id), dbus.String(data),
                                 dbus_interface=self.interface)

    def List(self):
        """list all loaded plugins"""
        return self.dbus.Service(dbus_interface='{0}.pluginmanager'.format(
                                                                self.vdr_addr))


class Recordings(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Recordings", 'recording')

    def Get(self, recording):
        """Get info about a recording - use it's number or path as argument"""
        return self.dbus.Get(recording, dbus_interface = self.interface,
                             signature='v')

    def List(self):
        """List recordings"""
        return self.dbus.List(dbus_interface=self.interface)

    def Play(self,recording, time=-1):
        """play a recording at time dbus.String('hh:mm:ss.f') or frame dbus.Int32(<frame>)
        If framenumber is -1, playing is resumed at the last saved position"""
        return self.dbus.Play(recording, time, dbus_interface = self.interface,
                                signature='vv')

    def AddExtraVideoDirectory(self, path):
        return self.dbus.AddExtraVideoDirectory(dbus.String(path),
                                                dbus_interface = self.interface)

    def DeleteExtraVideoDirectory(self, path):
        return self.dbus.DeleteExtraVideoDirectory(dbus.String(path),
                                                dbus_interface = self.interface)

    def ClearExtraVideoDirectories(self):
        return self.dbus.ClearExtraVideoDirectories(
                                                dbus_interface = self.interface)

    def ListExtraVideoDirectories(self):
        return self.dbus.ListExtraVideoDirectories(
                                                dbus_interface = self.interface)


class Remote(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Remote", 'remote')

    def Enable(self):
        """enable remote for VDR"""
        return self.dbus.Enable(dbus_interface = self.interface)

    def Disable(self):
        """disable remote for VDR"""
        return self.dbus.Disable(dbus_interface = self.interface)

    def Status(self):
        """show status of remote in VDR"""
        return self.dbus.Status(dbus_interface = self.interface)

    def HitKey(self, key):
        return self.dbus.HitKey(dbus.String(key),
                                dbus_interface = self.interface)

    def HitKeys(self, keylist):
        return self.dbus.HitKeys(dbus.Array(keylist, "s"),
                                 dbus_interface = self.interface, )
    def AskUser(self, title, items):
        """display list of strings on the osd and let the user select one"""
        return self.dbus.HitKey(dbus.String(title), dbus.Array(items, "s"),
                                dbus_interface = self.interface)
        ''' TODO: automatic callback for result
        The zero-based index of the selected item will be returned with the signal "AskUserSelect",
        the first parameter is the title-string, the second the index.
        An index of -1 means, no item is selected (or osd closed because of a timeout).
        '''

    def CallPlugin(self, plugin):
        """open the main menu entry of a plugin"""
        return self.dbus.CallPlugins(dbus.String(plugin),
                                dbus_interface = self.interface)

    def SwitchChannel(self, channel):
        """switch channel like SVDRP command CHAN. dbus.String:( +|-|<number>|<name>|<id>)"""
        return self.dbus.SwitchChannel(dbus.String(channel),
                                dbus_interface = self.interface)

    def SetVolume(self, volume):
        """set volume to dbus.String(<number 0 - 255>|+|-|mute)"""
        return self.dbus.SetVolume(dbus.String(volume),
                                   dbus_interface = self.interface)

    def GetVolume(self):
        """show volume level"""
        return self.dbus.GetVolume(dbus_interface = self.interface)


class Setup(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Setup", 'setup')

    def List(self):
        return self.dbus.List(dbus_interface = self.interface)

    def Get(self, parameter):
        """get setup parameter"""
        return self.dbus.Get(parameter, dbus_interface = self.interface)

    def Set(self, parameter, value):
        """set parameters to setup.conf
        Some parameters are known to be integers (look at setup.c) with a valid
        range. All others are handled as strings.
        WARNING: Be careful to set values unknown to dbus2vdr. It will trigger a reload
        of the whole setup.conf including calls to SetupParse of every plugin.
        This might have unexpected side effects!
        You may also get/set/delete parameters for plugins with
        'pluginname.parameter'
        but it is not guaranteed that it will work and that changes will affect the plugin's
        behaviour immediately.
        dbus2vdr will call the plugin's "SetupParse" function. If it returns true the value
        is stored in the setup.conf. You may need to restart vdr.
        """
        return self.dbus.Set(parameter, value, dbus_interface = self.interface,
                             signature='sv')

    def Del(self, parameter):
        """delete parameters from setup.conf
        delete all settings of one plugin: Setup.Del('pluginname.*')"""
        return self.dbus.Del(parameter, dbus_interface = self.interface)


class Shutdown(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Shutdown", 'shutdown')

    def ConfirmShutdown(self, ignore_user=False):
        return self.dbus.ConfirmShutdown(dbus.Boolean(ignore_user),
                                         dbus_interface = self.interface)

    def ManualStart(self):
        return self.dbus.ManualStart(dbus_interface = self.interface)

    def SetUserInactive(self):
        return self.dbus.SetUserInactive(dbus_interface = self.interface)


class Skin(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Skin", 'skin')

    def QueueMessage(self, message):
        return self.dbus.QueueMessage(dbus.String(message),
                                      dbus_interface = self.interface)

    def ListSkins(self):
        return self.dbus.ListSkins(dbus_interface = self.interface)

    def CurrentSkin(self):
        return self.dbus.CurrentSkin(dbus_interface = self.interface)

    def SetSkin(self, skin):
        return self.dbus.SetSkin(dbus.String(skin),
                                 dbus_interface = self.interface)


class Timers(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/Timers", 'timer')

    def List(self):
        return self.dbus.List(dbus_interface = self.interface)

    def Next(self):
        """The following is returned:
        int32   reply code (250 for success, 550 on error)
        int32   timer id (-1 if there's no timer at all)
        int32   'rel' seconds (see SVDRP NEXT REL)
        uint64  starttime in seconds since epoch (time_t format)
        uint64  stoptime in seconds since epoch (time_t format)
        string  title of the event"""
        return self.dbus.Next(dbus_interface = self.interface)

    def New(self, timer):
        return self.dbus.New(dbus.String(timer),
                             dbus_interface = self.interface)

    def Delete(self, id):
        return self.dbus.Delete(dbus.Int32(id),
                                dbus_interface = self.interface)


class vdr(DBusClass):
    def __init__(self, bus, instance=0):
        super().__init__(bus, "/vdr", 'vdr')

    def Status(self):
        return self.dbus.Status(dbus_interface = self.interface)
