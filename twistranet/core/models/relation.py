from django.db import models
from django.contrib.auth.models import User
from twistranet.core.models import Content
from twistranet.core.models import Account
# 
# class Relation(models.Model):
#     """
#     A relation describes what happens when two users 'meet'.
#     Kind of relations :
#     - Follow (asymetrical relation w/o approval)
#     - Network (symetrical relation w/ approval)
#     """
#     initiator = models.ForeignKey(Account, related_name = "initiator_whose")
#     target = models.ForeignKey(Account, related_name = "target_whose")
#     approved = models.BooleanField()        # True if the target approved the relation. 
#                                             # Used when security is restricted.
#     
#     def __unicode__(self):
#         return u"%s => %s (approved=%s)" % (self.initiator, self.target, self.approved, )
# 
#     class Meta:
#         app_label = 'twistranet'
#         unique_together = ("initiator", "target", )