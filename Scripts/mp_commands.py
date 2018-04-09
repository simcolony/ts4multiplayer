from update import output_irregardelessly as output
import services, sims4
import server.clientmanager
import distributor.system


@sims4.commands.Command('get_con', command_type=sims4.commands.CommandType.Live)
def get_con(_connection=None):
    #Gets the current client connection
    output = sims4.commands.CheatOutput(_connection) 
    output(str(_connection))
    
@sims4.commands.Command('get_clients', command_type=sims4.commands.CommandType.Live)
def get_clients(_connection=None):
    output = sims4.commands.CheatOutput(_connection) 
    clients = services.client_manager()._objects.values()    
    #Gets all the current client connections
    for client in clients:
        output(str(client.id))
        
@sims4.commands.Command('add_client_sims', command_type=sims4.commands.CommandType.Live)
def add_client_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection) 
    client = services.client_manager().get(1000)
    first_client = services.client_manager().get_first_client()
    #Add the first client's selectable sims to the new client's. Only expecst one multiplayer client at the moment.
    for sim in client._selectable_sims:
        output(str(sim))
    
    output(str(len(client._selectable_sims)))
    
    for sim_info in first_client._selectable_sims:
        client._selectable_sims.add_selectable_sim_info(sim_info)
    client.set_next_sim()
    
    
@sims4.commands.Command('cnc', command_type=sims4.commands.CommandType.Live)
def cnc(_connection=None):      
    #Create a new client. Deprecated.
    output = sims4.commands.CheatOutput(_connection) 
    client = services.client_manager().get_first_client()
    account = server.account.Account(865431, "Jon Snow")
    new_client = services.client_manager().create_client(1000, account, client._household_id)
    # new_client.clear_selectable_sims()
    # for sim_info in client._selectable_sims:
        # new_client._selectable_sims.add_selectable_sim_info(sim_info)
    # new_client.set_next_sim()

    output("Adding client")
    
@sims4.commands.Command('rem', command_type=sims4.commands.CommandType.Live)
def rem(_connection=None):      
    #Forcefully remove the multiplayer client. Only supports one multiplayer client at the moment. 
    output = sims4.commands.CheatOutput(_connection) 
    output("Attempting to remove client")
    distributor.system._distributor_instance.remove_client_from_id(1000)
    client_manager = services.client_manager()
    client = client_manager.get(1000)
    client_manager.remove(client)

    output("Removed client")
import socket
@sims4.commands.Command('get_name', command_type=sims4.commands.CommandType.Live)
def get_name(_connection=None):      
    output = sims4.commands.CheatOutput(_connection) 
    output(str(socket.gethostname()))

from protocolbuffers import FileSerialization_pb2 as serialization
import persistence_module
import services.persistence_service as ps
@sims4.commands.Command('load_zone', command_type=sims4.commands.CommandType.Live)
def load_zone(_connection=None):      
    try:
        zone_objects_pb = serialization.ZoneObjectData()
        zone_objects_message = open("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/saves/scratch/scratch_1248/zoneObjects-093e073e3fbb49ce-6.sav", "rb").read()
        # output("msg", dir(zone_objects_pb))
        zone_objects_pb.ParseFromString(zone_objects_message)
        # output("msg", zone_objects_pb)
        output("msg", dir(persistence_module))
        # output("msg", zone_objects_message)
        persistence_module.run_persistence_operation(persistence_module.PersistenceOpType.kPersistenceOpLoadZoneObjects, zone_objects_pb, 0, None)
        persistence_service = services.get_persistence_service()
        persistence_service.build_caches()
    except Exception as e:
        output("er", e)
        
import sys
@sims4.commands.Command('print_modules', command_type=sims4.commands.CommandType.Live)
def get_modules(_connection = None):
    for thing in sys.modules.keys():
        output("modules", thing)
        
import sims4.zone_utils
import _buildbuy
@sims4.commands.Command('stuff', command_type=sims4.commands.CommandType.Live)
def stuff(_connection = None):
    output("msg", dir(_buildbuy))
    
from world.travel_service import travel_sim_to_zone
@sims4.commands.Command('travel', command_type=sims4.commands.CommandType.Live)
def travel(_connection = None):
    client = services.client_manager().get_first_client()
    zone = services.current_zone()
    travel_sim_to_zone(client.active_sim.id, zone.id)