from ..congestion import Now
from ...packet_builder import QuicSentPacket

# a class to collect information about the rate sample
class RateSample:
    def __init__(self) -> None:
        self.packet_info = {} # store the informations about Transport controler when packet was sent
        self.delivered = 0
        self.lost = 0
        self.inflight = 0
        self.delivery_rate = 0
        self.app_limited = False
        self.lost_timestamp = None
        self.interval = 0

    def in_congestion_recovery(self, t):
        # check if we were in congestion recovery at time t
        return self.lost_timestamp != None and t > self.lost_timestamp

    def update_app_limited(self):
        # consider for the moment that there's no application limitation
        pass

    def sample_delivered(self):
        # let's just make something simple for now
        return self.delivered

    def get_packet_info(self, packet: QuicSentPacket):
        return self.packet_info[packet.packet_number]
    
    def add_packet_info(self, packet: QuicSentPacket):
        self.packet_info[packet.packet_number] = {
            "delivered" : self.delivered,
            "lost" : self.lost,
            "inflight" : self.inflight
        }

    def rm_packet_info(self, packet : QuicSentPacket):
        try:
            del self.packet_info[packet.packet_number]
        except:
            pass

    def time_elapsed(self, packet):
        # get the time elapsed since the sending of a packet (in seconds)
        return Now() + packet.sent_time - self.start_time
    
    def update_delivery_rate(self, packet):
        # update delivery rate
        self.delivery_rate = (self.delivered) / self.interval

    def on_ack(self, packet : QuicSentPacket):
        self.inflight -= max(packet.sent_bytes, 0)
        self.delivered += packet.sent_bytes
        
        self.update_delivery_rate(packet)
        self.rm_packet_info(packet)
        
    
    def on_sent(self, packet : QuicSentPacket):
        self.interval += 1
        self.inflight += packet.sent_bytes
        self.add_packet_info(packet)

    def on_expired(self, packet : QuicSentPacket):
        self.inflight - packet.sent_bytes
        self.rm_packet_info(packet)

    def on_lost(self, packet : QuicSentPacket):
        self.inflight -= packet.sent_bytes
        self.lost += packet.sent_bytes
        self.lost_timestamp = packet.sent_time
        self.update_delivery_rate(packet)