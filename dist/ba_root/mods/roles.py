effectCustomers = {}
customTag = {}
banList = {}
serverWhiteList = {}
customList = []
chatWhitelist = []
unKickable = []
toppersList = ['pb-IF40V1hYXQ==', 'pb-IF4gVE8TNw==']
vips = []
admins = []
special = {}
surroundingObjectEffect = []
sparkEffect = []
smokeEffect = []
scorchEffect = [] 
distortionEffect = []
glowEffect = [] 
iceEffect=[]
slimeEffect = []
metalEffect = []
dragonHashes = []
from administrator_setup import owners
chatWhitelist += owners + admins
unKickable += owners + admins

#Do not change the order,
#or else scripts will not work and shows error

#Read The following Where you can find what is used for what...

#'customList' are the people who can use profile Tag
#'customTag' is a dict with uniqueID and Tags which are used (For CoinSysytem cmd used by public)
#'serverWhiteList' is mostly used for PVT servers where only given people can join
#Or else they will be kicked
#'chatWhitelist' is used when chatWhitelistMode(in settings.py) is enabled, this
#will all only specified people to chat
#'unKickable' are people who can't be disconnected (except by 'owners')