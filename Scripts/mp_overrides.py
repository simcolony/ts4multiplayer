from update import output_irregardelessly as output
import services, glob, sims4, inspect, re
from server.client import Client
import distributor.distributor_service
import system_distributor
import server.account
import server.client
from distributor.system import Distributor
import distributor.system
from mp import is_client
from distributor.rollback import ProtocolBufferRollback
from protocolbuffers import Sims_pb2
from objects import ALL_HIDDEN_REASONS
from distributor.ops import GenericProtocolBufferOp
from protocolbuffers.DistributorOps_pb2 import Operation
import distributor.ops

def get_first_client(self): 
    # Get the original client instead of the stand-in client. Just in-case some EA code is finnicky with multiple clients. Only supports one
    # multiplayer client at the moment.
    for client in self._objects.values():
        if client.id == 1000:
            continue
        return client
        
    

def start(self):
    #Override the original function with one that creates a "SystemDistributor" instead of a regular old Distributor. 

    import animation.arb
    animation.arb.set_tag_functions(distributor.system.get_next_tag_id, distributor.system.get_current_tag_set)
    distributor.system._distributor_instance = system_distributor.SystemDistributor()



            
def on_add(self):
    #We override the on_add function of the clients so we can add the stand-in client at the same time. Only supports  one
    #multiplayer client at the moment, which has the id of 1000.
    if self.id != 1000:
        account = server.account.Account(865431, "Jon Snow")
        new_client = services.client_manager().create_client(1000, account, 0)
    for sim_info in self._selectable_sims:
        new_client._selectable_sims.add_selectable_sim_info(sim_info)
        new_client.set_next_sim()
    if self._account is not None:
        self._account.register_client(self)
    for sim_info in self._selectable_sims:
        self.on_sim_added_to_skewer(sim_info)
    distributor = Distributor.instance()
    distributor.add_object(self)
    distributor.add_client(self)
    self.send_selectable_sims_update()
    self.selectable_sims.add_watcher(self, self.send_selectable_sims_update)
    
    
def on_remove(self):
    #We override the on_remove function of the client so we can remove the stand-in client at the same time.
    #Only supports one multiplayer client at the moment, which has the id of 1000.
    if self.active_sim is not None:
        self._set_active_sim_without_field_distribution(None)
    if self._account is not None:
        self._account.unregister_client(self)
    for sim_info in self._selectable_sims:
        self.on_sim_removed_from_skewer(sim_info)
    self.selectable_sims.remove_watcher(self)
    distributor = Distributor.instance()
    distributor.remove_client(self)
    self._selectable_sims = None
    self.active = False
    if self.id != 1000:
        Distributor.instance().remove_client_from_id(1000)
        client_manager = services.client_manager()
        client = client_manager.get(1000)
        client_manager.remove(client)


def send_selectable_sims_update(self):
    msg = Sims_pb2.UpdateSelectableSims()
    for sim_info in self._selectable_sims:
        with ProtocolBufferRollback(msg.sims) as new_sim:
            new_sim.id = sim_info.sim_id
            career = sim_info.career_tracker.get_currently_at_work_career()
            new_sim.at_work = career is not None and not career.is_at_active_event
            new_sim.is_selectable = sim_info.is_enabled_in_skewer
            (selector_visual_type, career_category) = self._get_selector_visual_type(sim_info)
            new_sim.selector_visual_type = selector_visual_type
            if career_category is not None:
                new_sim.career_category = career_category
            new_sim.can_care_for_toddler_at_home = sim_info.can_care_for_toddler_at_home
            if not sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                new_sim.instance_info.zone_id = sim_info.zone_id
                new_sim.instance_info.world_id = sim_info.world_id
                new_sim.firstname = sim_info.first_name
                new_sim.lastname = sim_info.last_name
                zone_data_proto = services.get_persistence_service().get_zone_proto_buff(sim_info.zone_id)
                if zone_data_proto is not None:
                    new_sim.instance_info.zone_name = zone_data_proto.name
    distributor = Distributor.instance().get_client(self.id)
    distributor.add_op_with_no_owner(GenericProtocolBufferOp(Operation.SELECTABLE_SIMS_UPDATE, msg))

    
    
if not is_client:
    server.clientmanager.ClientManager.get_first_client = get_first_client

    distributor.distributor_service.DistributorService.start = start
    server.client.Client.on_add = on_add
    server.client.Client.on_remove = on_remove

    server.client.Client.send_selectable_sims_update = send_selectable_sims_update
