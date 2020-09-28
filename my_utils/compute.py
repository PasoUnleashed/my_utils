from abc import ABC,abstractmethod
from my_utils import util
import threading
import queue
from enum import Enum
# Implement stop commmand
# Implement status update first


class Status(Enum):
    RUNNING = 0
    STOPPED = 1
    STOPPING = 2
class UpdateType(Enum):
    STATUS = 0
class CommandType(Enum):
    STOP = 0
    ADD_INPUT = 1
    ADD_OUTPUT = 2
    ADD_CHILD = 3
    REMOVE_CHANNEL =4
    REMOVE_CHILD = 5
class DataPacket:
    def __init__(self,sender,data):
        self.sender= sender
        self.data = data
class ComputationUnitUpdate:
    pass
class ComputationUnitCommand:
    def __init__(self,t,data):
        self.type = t
        self.data=data
class ComputationalUnit:
    def __init__(self,name,parent=None,output_to_host=False):
        self.name = name
        if(parent==None):
            self.parent=None
        else:
            self.parent=parent
        self.host_channel = Channel(self.name)
        self.status = Status.STOPPED
        self._isunit = False
        self._run_thread=None
        self.data_output_channels =[]
        self.data_input_channels = []
        self.children = []
        self.output_to_host=output_to_host
    def start(self):
        if(self._run_thread!=None):
            while self._run_thread.is_alive():
                pass
        self._run_thread = threading.Thread(target=self._run,name=self.name)
        self.status = Status.RUNNING
        self._run_thread.start() 
    def stop(self,wait=False):
        if(self._isunit):
            self.status=Status.STOPPING
        else:
            self.status=Status.STOPPING
            self.host_channel.send_command(ComputationUnitCommand(CommandType.STOP,''))
            while(self.is_running() and wait):
                pass
            if(not self.is_running()):
                self.status=Status.STOPPED
    def consume_channels(self):
        return self._consume_channels()
    def _consume_channels(self):
        data_acum = []
        command_acum = []
        self.host_channel.update()
        data_acum+=self.host_channel.get_all_data()
        command_acum+=self.host_channel.get_all_commands()
        rem = []
        for i in self.data_input_channels:
            if(i.is_open):
                i.update()
                data_acum+=i.get_all_data()
                command_acum+=i.get_all_commands()
            else:
                rem.append(i)
        for i in self.data_output_channels:
            if(i.is_open):
                i.update()
                data_acum+=i.get_all_data()
                command_acum+=i.get_all_commands()
            else:
                rem.append(i)
        for i in rem:
            if(i in self.data_input_channels):
                self.data_input_channels.remove(i)
            elif(i in self.data_output_channels):
                self.data_output_channels.remove(i)
        remchild = []
        for i in self.children:
            i.host_channel.update()
            data_acum+=i.host_channel.get_all_data()
            command_acum+=i.host_channel.get_all_commands()
        for i in remchild:
            self.remove_child_unit(i)
        return data_acum,command_acum
    def _handle_channels(self):
        data_acum,command_acum = self._consume_channels()
        for i in command_acum:
            self._handle_command(i)
        for i in data_acum:
            self.handle_data(i)
    def _run(self):
        self.on_start()
        self._isunit = True
        while self.status==Status.RUNNING:
            self._handle_channels()
            self.update()
        self._on_stop()
        self.status=Status.STOPPED
    def manual_loop_iteration(self):
        self._handle_channels()
    def _send_update(self):
        pass
    def output_data(self,data):
        send = data
        if(not isinstance(data,DataPacket)):
            send = DataPacket(self.name,data)
        for i in self.data_output_channels:
            i.send_data(send)
        if(self.output_to_host):
            self.host_channel.send_data(send)
    def output_data_to_host(self,data):
        send = data
        if(not isinstance(data,DataPacket)):
            send = DataPacket(self.name,data)
        self.host_channel.send_data(send)
    def add_input_channel(self,channel):
        self.data_input_channels.append(channel)
        if(threading.current_thread().name!=self.name and self.status==Status.RUNNING):
            self.host_channel.send_command(ComputationUnitCommand('add_input',channel))
    def create_output_channel(self):
        channel = Channel(self.name)
        self.data_output_channels.append(channel)
        if(threading.current_thread().name!=self.name and self.status==Status.RUNNING):
            self.host_channel.send_command(ComputationUnitCommand('add_output',channel))
        return channel
    def is_running(self):
        if(self._run_thread==None or not self._run_thread.is_alive()):
            return False
        return True
    def add_child_unit(self,unit):
        self.children.append(unit)
        if(not self._isunit and self.status==Status.RUNNING):
            self.host_channel.send_command(ComputationUnitCommand(CommandType.ADD_CHILD,unit))
    def remove_child_unit(self,unit):
        unit.stop()
        rem=[]
        for i in self.children:
            if(i.name==unit.name):
                rem.append(i)
        if(len(rem)==0):
            return
        for i in rem:
            self.children.remove(i)
        if(not self._isunit and self.status==Status.RUNNING):
            self.host_channel.send_command(ComputationUnitCommand(CommandType.REMOVE_CHILD,unit))
        else:
            self.host_channel.send_command(ComputationUnitCommand(CommandType.REMOVE_CHILD,unit))        
    def remove_channels(self,owner_name):
        rem = []
        for i in self.data_input_channels:
            if(i.owner_name==owner_name):
                rem.append(i)
        for i in rem:
            i.close()
            self.data_input_channels.remove(i)
        rem = []
        for i in self.data_output_channels:
            if(i.owner_name ==owner_name):
                rem.append(i)
        for i in rem:
            i.close()
            self.data_output_channels.remove(i)
        if(not self._isunit and self.status==Status.RUNNING):
            self.host_channel.send_command(ComputationUnitCommand(CommandType.REMOVE_CHANNEL,owner_name))
    def _handle_command(self,command):
        intercepted_types = [1,2]
        if(isinstance(command.type,int)):
            if(command.type == CommandType.ADD_INPUT):
                self.data_input_channels.append(command.data)
            elif(command.type == CommandType.ADD_OUTPUT):
                self.data_output_channels.append(command.data)
            elif(command.type == CommandType.ADD_CHILD):
                self.children.append(command.data)
            elif(command.type == CommandType.STOP):
                self.stop()
            elif(command.type== CommandType.REMOVE_CHANNEL):
                self.remove_channels(command.data)
            elif(command.type==CommandType.REMOVE_CHILD):
                self.remove_child_unit(command.data)
        else:
            self.handle_command(command)
    def _handle_update(self,update):
        pass
    def _on_stop(self):
        print(f'{self.name} stopped')
        for i in self.children:
            print(f"Stopping child unit: {i.name}")
            i.stop()
        for i in self.data_output_channels:
            i.close()
        for i in self.data_input_channels:
            i.close()
        self.host_channel.close()
        self.on_stop()
    @abstractmethod
    def handle_data(self,data):
        pass
    @abstractmethod
    def handle_command(self,command):
        pass
    @abstractmethod
    def on_stop(self):
        pass
    @abstractmethod
    def on_start(self):
        pass
    @abstractmethod
    def update(self):
        pass
class ChannelUpdateType(Enum):
    CLOSE = 1
class Channel:
    def __init__(self,owner_name):
        self.owner_name = owner_name
        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()
        self.data=[]
        self.updates = []
        self.commands = []
        self.is_open = True
    def has_update(self):
        return bool(self.updates)
    def get_update(self):
        if(self.has_update()):
            return self.updates.pop(0)
    def get_all(self):
        return self.get_all_data(),self.get_all_commands(),self.get_all_updates()
    def get_all_updates(self):
        ret = self.updates
        self.updates=[]
        return ret
    def has_command(self):
        return bool(self.commands)
    def get_command(self):
        if(len(self.commands>0)):
            return self.commands.pop(0)
    def get_all_commands(self):
        ret = self.commands
        self.commands=[]
        return ret
    def has_data(self):
        return bool(self.data)
    def get_data(self):
        if(len(self.data)>0):
            return self.data.pop(0)
    def get_all_data(self):
        ret = self.data
        self.data=[]
        return ret
    def _is_target(self):
        if(threading.current_thread().name==self.owner_name):
            return True
        return False
    def update(self):
        if(self._is_target()):
            incoming = self.outgoing
            outgoing = self.incoming
        else:
            incoming = self.incoming
            outgoing = self.outgoing
        if(not incoming.empty()):
            typ,data = incoming.get()
            if(typ=='d'):
                self.data.append(data)
            elif(typ=='u'):
                self.updates.append(data)
            elif(typ=='c'):
                self.commands.append(data)
            elif(typ=='h'):
                if(data==ChannelUpdateType.CLOSE):
                    self.is_open==False
    def close(self):
        self._send_tuple(('h',ChannelUpdateType.CLOSE))
        self.is_open=False
    def send_command(self,command):
        tup = ('c',command)
        self._send_tuple(tup)
    def send_update(self,update):
        tup = ('u',update)
        self._send_tuple(tup)
    def send_data(self,data):
        tup = ('d',data)
        self._send_tuple(tup)
    def _send_tuple(self,i):
        if(self._is_target()):
            outgoing = self.incoming
        else:
            outgoing = self.outgoing
        if(not self.is_open):
            return
        outgoing.put(i) 
class DataPrinterUnit(ComputationalUnit):
    def __init__(self,name,lmbda = lambda x: x, parent=None):
        super().__init__(name,parent=parent)
        self.lmbda=lmbda
    def handle_data(self,data):
        print(f"{data.sender}: {self.lmbda(data.data)}")
    def handle_command(self,command):
        pass
    def on_stop(self):
        pass
    def on_start(self):
        pass
    def update(self):
        pass
class DataMaker(ComputationalUnit):
    def __init__(self,name, parent=None):
        super().__init__(name,parent=parent)
        self.message = 'Hello'
    def handle_data(self,data):
        self.output_data(reversed(data.data))
    def handle_command(self,command):
        pass
    def on_stop(self):
        pass
    def on_start(self):
        pass
    def update(self):
        self.i=self.i+1
        self.output_data(self.i)


