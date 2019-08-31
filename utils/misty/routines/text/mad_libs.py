import asyncio
import operator
from contextlib import suppress
from functools import reduce
from itertools import count
from random import choice

import spacy
from misty_py.utils import wait_in_order
from more_itertools import interleave_longest, always_iterable, first

from utils.misty.core import Routine, _TTSOption

__author__ = 'acushner'


class _MadLibsWords(Routine):
    """words from a simpsons episode classified into parts of speech and tags using spacy"""

    def __init__(self):
        super().__init__('TOK__')
        self.ADJ__JJ = ['able', 'absolute', 'airborne', 'alcoholic', 'alive', 'alternative', 'amazed', 'animatronic',
                        'antagonistic', 'appreciative', 'average', 'back', 'bad', 'barbed', 'barbeque', 'beautiful',
                        'big', 'black', 'blue', 'brown', 'bunly', 'certain', 'chinny', 'chopped', 'close', 'cold',
                        'colored', 'conga', 'conscious', 'cool', 'corporate', 'corresponding', 'courtesy', 'crappy',
                        'crazy', 'curious', 'cute', 'dead', 'delicious', 'different', 'dirty', 'disappointing',
                        'disgusting', 'displeased', 'doubtless', 'downstream', 'easy', 'educational', 'empty', 'enough',
                        'entire', 'eternal', 'evil', 'exact', 'excellent', 'extra', 'few', 'fifth', 'first', 'flat',
                        'flipped', 'fluid', 'former', 'fourth', 'free', 'ful', 'full', 'funny', 'garlic', 'glorious',
                        'good', 'gray', 'great', 'green', 'haired', 'handed', 'happy', 'hard', 'hasty', 'heady',
                        'healthy', 'heavy', 'high', 'hilarious', 'horrible', 'hot', 'huge', 'hungry', 'ignorant',
                        'imaginary', 'independent', 'instrumental', 'jewish', 'klaxon', 'large', 'last', 'left',
                        'lentil', 'little', 'local', 'lonely', 'long', 'loving', 'low', 'lush', 'magical', 'major',
                        'many', 'mechanical', 'modern', 'moral', 'mouthful', 'much', 'naked', 'new', 'next', 'nice',
                        'non', 'normal', 'nth', 'nuclear', 'obvious', 'okay', 'old', 'only', 'open', 'orange',
                        'original', 'other', 'overall', 'own', 'pale', 'pet', 'plain', 'poodle', 'poor', 'preachy',
                        'predictable', 'prehistoric', 'previous', 'public', 'quiet', 'raw', 'real', 'relative',
                        'religious', 'respectable', 'rich', 'right', 'robotic', 'rotissory', 'runaway', 'same',
                        'satisfied', 'scientician', 'second', 'secret', 'seventh', 'several', 'sexual', 'shameless',
                        'shortened', 'silent', 'silhouetted', 'similar', 'slimy', 'slow', 'solid', 'song', 'sorry',
                        'special', 'square', 'startled', 'steep', 'strong', 'sublime', 'such', 'super', 'sure',
                        'surprised', 'technical', 'thankless', 'thingy', 'token', 'top', 'true', 'unlucky',
                        'unsanitary', 'up', 'useless', 'usual', 'various', 'vegetable', 'vegetarian', 'veggie', 'white',
                        'whole', 'wild', 'wonderful', 'worthy', 'wrong', 'yellow']
        self.ADJ__JJR = ['closer', 'greater', 'higher', 'lighter', 'more', 'pacifier', 'shorter', 'smaller', 'snappier',
                         'warmer']
        self.ADJ__JJS = ['best', 'cutest', 'greatest', 'largest', 'least', 'most', 'nearest', 'smallest']
        self.ADP__IN = ['about', 'above', 'across', 'after', 'against', 'along', 'although', 'around', 'as', 'at',
                        'because', 'before', 'behind', 'beside', 'between', 'by', 'cause', 'de', 'down', 'due',
                        'during', 'except', 'for', 'from', 'if', 'in', 'into', 'like', 'near', 'of', 'on', 'onto',
                        'out', 'outside', 'over', 'since', 'than', 'that', 'though', 'through', 'to', 'toward',
                        'towards', 'uncovers', 'under', 'until', 'up', 'whether', 'while', 'with', 'without']
        self.ADV__EX = ['there']
        self.ADV__RB = ['absolutely', 'actually', 'after', 'again', 'ago', 'ahead', 'alike', 'all', 'almost', 'along',
                        'also', 'always', 'anymore', 'apparently', 'appropriately', 'as', 'away', 'back', 'backwards',
                        'badly', 'before', 'behind', 'besides', 'certainly', 'characteristically', 'course', 'cud',
                        'curly', 'derisively', 'diddily', 'doodily', 'doogily', 'doubt', 'down', 'downhill', 'drolly',
                        'enough', 'entirely', 'equally', 'especially', 'even', 'ever', 'everywhere', 'evilly',
                        'exactly', 'far', 'fast', 'feebly', 'first', 'freshly', 'further', 'hard', 'here', 'hidely',
                        'home', 'hoover', 'however', 'in', 'indeed', 'individually', 'instead', 'invariably', 'just',
                        'kind', 'lately', 'later', 'long', 'loud', 'maybe', 'mistakenly', 'much', 'musically', 'nearly',
                        'never', 'next', 'not', 'now', 'nowhere', 'of', 'off', 'often', 'okily', 'on', 'once', 'only',
                        'out', 'over', 'overall', 'parsely', 'perfectly', 'perhaps', 'poorly', 'possibly', 'pretty',
                        'quietly', 'quite', 'radically', 'rather', 'really', 'repeatedly', 'right', 'secondly',
                        'seriously', 'silently', 'simply', 'singly', 'so', 'somewhat', 'still', 'strictly',
                        'strikingly', 'strongly', 'suddenly', 'syrup', 'then', 'there', 'therefore', 'though',
                        'through', 'together', 'too', 'truly', 'unfortunately', 'up', 'uproariously', 'upward',
                        'upwards', 'usually', 'very', 'visibly', 'way', 'wearily', 'well', 'whatsoever', 'wildly',
                        'wistfully', 'worriedly', 'yet']
        self.ADV__RBR = ['closer', 'less', 'longer', 'more']
        self.ADV__RBS = ['most']
        self.ADV__WRB = ['how', 'when', 'whenever', 'where', 'why']
        self.AUX__MD = ['ca', 'could', 'should', 'wo']
        self.CCONJ__CC = ['and', 'both', 'but', 'or', 'yet']
        self.DET__DT = ['all', 'an', 'another', 'any', 'both', 'each', 'every', 'no', 'some', 'that', 'the', 'these',
                        'this', 'those']
        self.DET__PDT = ['all', 'half', 'quite']
        self.DET__PRPdollarsign = ['her', 'his', 'its', 'my', 'our', 'their', 'your']
        self.DET__WDT = ['that', 'whatever', 'which']
        self.INTJ__UH = ['ah', 'apu', 'aw', 'cf', 'eh', 'gosh', 'ha', 'hah', 'hello', 'hey', 'hi', 'hoover', 'huh',
                         'like', 'my', 'ned', 'no', 'oh', 'ok', 'okay', 'ooohhh', 'please', 'rl', 'sorry', 'sure',
                         'well', 'whoa', 'wow', 'yeah', 'yes']
        self.NOUN__NN = ['act', 'adult', 'advice', 'affair', 'agitator', 'air', 'airdate', 'alligator', 'ambiguity',
                         'amusement', 'animal', 'animation', 'anything', 'appearance', 'appetite', 'apple',
                         'appreciation', 'apu', 'arm', 'attention', 'attitude', 'autocannibalism', 'awe', 'axe', 'baaa',
                         'baaaaaad', 'baby', 'back', 'background', 'backyard', 'bacon', 'balloon', 'bar', 'barbecue',
                         'barbeque', 'barney', 'bat', 'bay', 'bbq', 'beard', 'beatnik', 'beaver', 'bed', 'beef', 'beer',
                         'belt', 'bill', 'billboard', 'billing', 'bird', 'bit', 'blackboard', 'book', 'boot', 'borsht',
                         'bottle', 'bowl', 'boy', 'br', 'brain', 'breakfast', 'breast', 'bridge', 'broiler', 'brush',
                         'bubble', 'bun', 'bunch', 'burger', 'bush', 'button', 'cadence', 'cafeteria', 'calendar',
                         'camel', 'camera', 'can', 'car', 'care', 'carnivore', 'carrot', 'cartoon', 'case', 'cash',
                         'castration', 'catch', 'celebrity', 'celery', 'chain', 'chalk', 'chance', 'character', 'cheer',
                         'cheese', 'chicken', 'child', 'chin', 'chock', 'chomp', 'chop', 'chunk', 'cigarette', 'clap',
                         'class', 'classroom', 'clock', 'clockwise', 'closing', 'cloud', 'clove', 'code', 'color',
                         'comedy', 'compilation', 'conclusion', 'continuity', 'conveyor', 'cooler', 'couch', 'council',
                         'counter', 'country', 'course', 'courtesy', 'courtroom', 'cow', 'crack', 'crank', 'crap',
                         'creature', 'credit', 'crowd', 'cuckoo', 'cum', 'cup', 'cuteness', 'cuter', 'cutoff', 'cutout',
                         'dad', 'dam', 'dance', 'dancing', 'day', 'ddg', 'death', 'deer', 'definition', 'density',
                         'desk', 'devil', 'dextrorsus', 'dh2', 'diagnosis', 'dialog', 'dialogue', 'didlyos',
                         'difference', 'dilemma', 'dinner', 'disaster', 'dog', 'dokily', 'dong', 'door', 'doris',
                         'dragon', 'dress', 'drive', 'edge', 'electricity', 'elf', 'end', 'ending', 'engine',
                         'enlightenment', 'enthusiasm', 'episode', 'euuuwww', 'everybody', 'everyone', 'everything',
                         'exception', 'eye', 'eyeball', 'face', 'fact', 'factory', 'faith', 'family', 'faq', 'fat',
                         'father', 'fault', 'fb', 'feed', 'feeling', 'fence', 'field', 'film', 'finger', 'flight',
                         'floor', 'fluid', 'folk', 'food', 'force', 'forehead', 'fork', 'form', 'forum', 'frame',
                         'franchise', 'friend', 'front', 'fun', 'funniest', 'fur', 'gag', 'gagfest', 'garage', 'garden',
                         'gazpacho', 'gelatin', 'glass', 'globe', 'goat', 'goodness', 'googily', 'gorilla', 'grade',
                         'grain', 'grampa', 'grating', 'grill', 'ground', 'growl', 'guest', 'gum', 'guy', 'haah',
                         'habit', 'hair', 'ham', 'hand', 'handcart', 'haven', 'head', 'hedge', 'height', 'helicopter',
                         'hill', 'hind', 'history', 'hl', 'hold', 'home', 'homeboy', 'homer', 'honey', 'host', 'hour',
                         'house', 'human', 'humor', 'hunk', 'hurt', 'hurter', 'ice', 'idea', 'image', 'in',
                         'ingredient', 'injection', 'inscription', 'interest', 'interior', 'intro', 'invitation',
                         'island', 'it', 'jack', 'jar', 'journey', 'kb', 'keg', 'kid', 'kiddie', 'killing',
                         'kind', 'kitchen', 'knife', 'know', 'lack', 'lamb', 'lamp', 'laude', 'lawn', 'leaf', 'left',
                         'leg', 'legend', 'length', 'lentil', 'lettuce', 'life', 'linda', 'line', 'lion', 'lisa',
                         'llama', 'load', 'loaf', 'lot', 'loudspeaker', 'lunch', 'machine', 'majority', 'man',
                         'manhole', 'marge', 'market', 'material', 'mean', 'meat', 'medium', 'message', 'microscope',
                         'middle', 'mind', 'minus', 'minute', 'mom', 'moment', 'monkey', 'monster', 'moo', 'morning',
                         'moron', 'mother', 'mouth', 'movie', 'mower', 'music', 'name', 'nancy', 'nature',
                         'neighborino', 'news', 'niece', 'night', 'nobody', 'noise', 'none', 'nooooo', 'north', 'nose',
                         'nothing', 'number', 'nursery', 'oasis', 'obfuscation', 'objection', 'obsession', 'oculus',
                         'office', 'oil', 'one', 'onion', 'ooh', 'oooh', 'ooooh', 'opening', 'orphanage', 'os',
                         'outline', 'ox', 'pacing', 'packing', 'paint', 'pan', 'park', 'part', 'party', 'passion',
                         'paul', 'peek', 'pellet', 'pepper', 'period', 'permission', 'petting', 'phone', 'phrase',
                         'picture', 'piece', 'pig', 'pigeon', 'piggs', 'piggyback', 'place', 'plan', 'plant', 'plate',
                         'plot', 'plug', 'population', 'porcine', 'pork', 'power', 'presciption', 'pressure', 'privacy',
                         'problem', 'product', 'production', 'projection', 'propaganda', 'property', 'quality',
                         'quarter', 'queasy', 'question', 'raccoon', 'race', 'rain', 'ranch', 'rapist', 'rat', 'recipe',
                         'reference', 'refuge', 'rendition', 'resistance', 'resolve', 'respect', 'rest', 'restriction',
                         'reunion', 'revenge', 'reverse', 'revision', 'rhyme', 'rhythm', 'ride', 'rider', 'right',
                         'ripeness', 'rivalry', 'river', 'rl', 'road', 'roast', 'rock', 'roof', 'rooftop', 'room',
                         'round', 'row', 'rush', 'sake', 'salad', 'salt', 'sarcasm', 'sausage', 'scene', 'school',
                         'scientician', 'screen', 'season', 'senor', 'sensibility', 'sequence', 'series', 'set',
                         'shade', 'shape', 'shark', 'shirt', 'show', 'side', 'sigh', 'sign', 'silhouette', 'sing',
                         'sinister', 'siren', 'skinner', 'sky', 'slam', 'slash', 'sleep', 'slh', 'slient', 'slope',
                         'slug', 'snake', 'snuh', 'solution', 'somebody', 'someone', 'something', 'song', 'soup',
                         'spider', 'spillway', 'spinning', 'spirit', 'spoon', 'spray', 'squirrel', 'staircase', 'state',
                         'statue', 'steel', 'stock', 'stomach', 'store', 'story', 'storyline', 'storytown', 'street',
                         'stroll', 'student', 'stuff', 'success', 'summa', 'summary', 'superstar', 'swap', 'switch',
                         'syndication', 'syrup', 'table', 'tablespoon', 'tail', 'tee', 'terri', 'theatre', 'theme',
                         'thing', 'thought', 'throught', 'time', 'title', 'toast', 'tofu', 'tomato', 'tongue',
                         'tonight', 'tool', 'top', 'town', 'tractor', 'traffic', 'train', 'trash', 'tray', 'treat',
                         'tree', 'treehouse', 'triangulation', 'tripe', 'troy', 'truck', 'truth', 'tube', 'tune',
                         'tunnel', 'tv', 'type', 'typo', 'uuh', 'uuuh', 'vegetable', 'vegetarian', 'vegetarianism',
                         'veggieback', 'video', 'viking', 'village', 'violence', 'vision', 'vocab', 'voice', 'waste',
                         'watch', 'water', 'way', 'weiner', 'while', 'whiny', 'whole', 'whopper', 'wife', 'wiggum',
                         'window', 'wire', 'wolf', 'woman', 'word', 'work', 'world', 'worm', 'wrecking', 'wriggling',
                         'wrong', 'yelling', 'zoo']
        self.NOUN__NNS = ['90s', 'acts', 'ages', 'alarms', 'angles', 'animals', 'arms', 'arrows', 'articles', 'authors',
                          'babies', 'barrels', 'bears', 'beliefs', 'binoculars', 'bites', 'boards', 'boxes', 'boys',
                          'braces', 'burgers', 'byobb', 'carnivores', 'carrots', 'cars', 'cartoons', 'cattle', 'causes',
                          'cents', 'changes', 'checks', 'cheers', 'children', 'chops', 'chuckles', 'chunks', 'cities',
                          'claps', 'classrooms', 'clothes', 'colors', 'commercials', 'contents', 'cops', 'covers',
                          'cows', 'credits', 'cries', 'crusades', 'cups', 'cuts', 'dances', 'days', 'deer', 'degrees',
                          'dogs', 'dollars', 'donuts', 'doorknob', 'downwards', 'drunks', 'ears', 'ellipses', 'entrees',
                          'episodes', 'errors', 'expectations', 'eyes', 'familes', 'feet', 'festivities', 'films',
                          'fingers', 'firecrackers', 'flanders', 'flips', 'fools', 'friends', 'fruits', 'gags', 'gasps',
                          'giants', 'giggles', 'glasses', 'goldilocks', 'goofs', 'grains', 'groans', 'guests', 'guys',
                          'hairs', 'hands', 'horns', 'hours', 'images', 'ingredients', 'instructions', 'invitations',
                          'invitiations', 'items', 'jockeys', 'jokes', 'kids', 'kinds', 'lakes', 'lands', 'lanes',
                          'laughs', 'leaves', 'legs', 'lentils', 'letters', 'licks', 'lines', 'lips', 'lots', 'lyrics',
                          'meals', 'members', 'messages', 'minutes', 'misidentifies', 'misinterprets', 'moments',
                          'mouths', 'moves', 'movies', 'neighbors', 'observations', 'occasions', 'others', 'pairs',
                          'pants', 'parents', 'parodies', 'partners', 'parts', 'pearls', 'pellets', 'people', 'pigs',
                          'places', 'plants', 'plates', 'points', 'poles', 'policies', 'printers', 'problems',
                          'questions', 'quotes', 'readers', 'reappears', 'references', 'relatives', 'rhymes', 'rights',
                          'roads', 'rumors', 'sausages', 'scalpels', 'scenes', 'schoolkids', 'schools', 'scissors',
                          'seats', 'sheep', 'shoes', 'sides', 'signs', 'smithers', 'socks', 'sounds', 'speakers',
                          'species', 'sprayers', 'squints', 'stairs', 'stars', 'starts', 'statues', 'steers', 'sticks',
                          'stripes', 'students', 'suggestions', 'sweaters', 'tablas', 'tablespoons', 'talks', 'thanks',
                          'thieves', 'things', 'trees', 'trips', 'utensils', 'vegetables', 'voices', 'wings', 'wives',
                          'words', 'worms', 'wrecks', 'writers', 'years']
        self.NUM__CD = ['101', '102', '104', '105', '106', '107', '109', '110', '111', '112', '115', '116', '119', '12',
                        '150', '1973', '1977', '1997', '20', '2010', '26', '27', '32', '52', '53', '57', '58', '61',
                        '62', '63', '65', '67', '68', '70', '71', '75', '85', '92', '96', '97', '99', 'eight',
                        'million', 'one', 'sixty', 'three', 'two']
        self.PART__RP = ['back', 'down', 'in', 'off', 'on', 'out', 'over', 'up']
        self.PART__TO = ['to']
        self.PRON__PRP = ['he', 'her', 'herself', 'him', 'himself', 'i', 'it', 'me', 'she', 'them', 'themselves',
                          'they', 'us', 'we', 'ya', 'yoooooou', 'you', 'yourself']
        self.PRON__WP = ['what', 'who']
        self.PROPN__NNP = ['7g04', 'aaaahhh', 'aaah', 'aaron', 'abe', 'act', 'adam', 'alamo', 'alarm', 'albany',
                           'alcoholic', 'alden', 'animation', 'apu', 'arrival', 'aw', 'azaria', 'babe', 'baby',
                           'barney', 'bart', 'bbbq', 'bbq', 'bear', 'beatle', 'beatles', 'beaumarchais', 'beef', 'beep',
                           'beer', 'bemidji', 'biology', 'blue', 'bo', 'bob', 'bobby', 'bond', 'bovine', 'bowman',
                           'brainerd', 'briere', 'briskly', 'brooks', 'buenos', 'bunyan', 'burger', 'burns', 'cabin',
                           'capsule', 'carl', 'cartwright', 'castellaneta', 'chain', 'charrick', 'cherry', 'chicken',
                           'chief', 'cigarettes', 'cohen', 'collier', 'collins', 'congratulations', 'considering',
                           'contributors', 'copper', 'copyright', 'couch', 'council', 'cow', 'cows', 'crestfallen',
                           'crosby', 'crowd', 'cut', 'dad', 'dan', 'daniel', 'david', 'de', 'dear', 'deer', 'del',
                           'ding', 'dog', 'dominik', 'don', 'doris', 'drive', 'eat', 'eddie', 'elementary', 'elizabeth',
                           'erik', 'escape', 'esophagus', 'eyeballer', 'fallin', 'family', 'father', 'film', 'flanders',
                           'flavored', 'food', 'fred', 'frederic', 'freedom', 'freeze', 'fujimoto', 'fun', 'future',
                           'galaxy', 'garden', 'gary', 'george', 'gettin', 'giblet', 'god', 'goldberg', 'goober',
                           'goose', 'gordon', 'gourmet', 'grade', 'grampa', 'grande', 'grau', 'grave', 'great',
                           'groundskeeper', 'guest', 'guests', 'guide', 'halas', 'ham', 'hank', 'harry', 'hartman',
                           'hayden', 'haynes', 'head', 'hendon', 'hey', 'hhg', 'hibbert', 'hiker', 'hill', 'hitch',
                           'hmmph', 'ho', 'hoek', 'homer', 'homes', 'homey', 'hoover', 'hot', 'idaho', 'independent',
                           'india', 'itchy', 'jack', 'james', 'janey', 'janie', 'jay', 'jimmy', 'john', 'jose',
                           'jp', 'julie', 'julius', 'jussi', 'kavner', 'kb', 'kevin', 'killer', 'kirkland', 'krabappel',
                           'krusty', 'kwik', 'lady', 'lafaurie', 'lake', 'lamb', 'laramie', 'larson', 'laughs', 'lee',
                           'leeesaaaa', 'lenny', 'lentil', 'limbo', 'linda', 'lipkin', 'lisa', 'little', 'log', 'lord',
                           'lou', 'lovejoy', 'lucifer', 'lunch', 'lunchlady', 'macarthur', 'macneille', 'magazines',
                           'maggie', 'maharishi', 'man', 'march', 'marge', 'mark', 'mart', 'matteson', 'maude',
                           'mcauley', 'mccartney', 'mccartneys', 'mcclure', 'mcniblets', 'meat', 'mel', 'midwest',
                           'milhouse', 'minnesota', 'minus', 'miss', 'missus', 'moe', 'monty', 'mother', 'mouth',
                           'movie', 'muffet', 'ned', 'negative', 'new', 'non', 'nooo', 'nooooo', 'norway', 'number',
                           'obligatory', 'octopus', 'od', 'off', 'ohh', 'ohhh', 'ohhhh', 'okay', 'old', 'on', 'ooh',
                           'ooohh', 'opening', 'original', 'os', 'otto', 'ox', 'pakkanen', 'pamela', 'parasite', 'park',
                           'passes', 'patty', 'paul', 'peep', 'petting', 'phil', 'piggy', 'pot', 'potato', 'premiere',
                           'president', 'previous', 'principal', 'puente', 'ralph', 'ren', 'reunion', 'revere',
                           'reverend', 'reviews', 'ricardo', 'rl', 'roberds', 'rock', 'ronstadt', 'roswell', 'rump',
                           'russi', 'russia', 'salibury', 'salisbury', 'sarcastically', 'scene', 'scott', 'scratchy',
                           'selma', 'sensible', 'series', 'sgt', 'shearer', 'shelbyville', 'sheri', 'sherri', 'silent',
                           'simpson', 'simpsonmobile', 'simpsons', 'sir', 'skidd', 'skinner', 'slh', 'smith', 'snaps',
                           'snpp', 'someone', 'springfield', 'starring', 'storytown', 'summary', 'sylvia', 'taylor',
                           'tc', 'terri', 'thistlewick', 'thought', 'three', 'timid', 'tito', 'tm', 'toddlerville',
                           'tofu', 'tom', 'tommy', 'tony', 'tress', 'trolley', 'trolly', 'troy', 'try', 'two', 'uhh',
                           'uhhh', 'umm', 'university', 'useless', 'uter', 'uuuh', 'varhola', 'vegetarian', 'village',
                           'voice', 'washington', 'welll', 'west', 'whaaat', 'whoa', 'wiggum', 'willie', 'willy',
                           'winfield', 'winn', 'wolf', 'woods', 'worker', 'worm', 'wreck', 'wsb', 'yantosca',
                           'yeardley', 'yo', 'york', 'yours', 'yum', 'zanfardino', 'zoo']
        self.PROPN__NNPS = ['balls', 'bananas', 'bears', 'burns', 'comments', 'equals', 'flanders', 'lievens', 'quotes',
                            'simpsons', 'smithers', 'sprayers', 'vegetarians', 'yells']
        self.VERB__MD = ['can', 'could', 'may', 'might', 'must', 'should', 'will', 'would']
        self.VERB__VB = ['agree', 'apocalypse', 'apologize', 'appear', 'appreciate', 'ask', 'be', 'believe', 'bite',
                         'bloooow', 'boast', 'break', 'bring', 'cafeteria', 'call', 'chew', 'come', 'condone', 'couch',
                         'cough', 'cut', 'defend', 'devote', 'die', 'disguise', 'dissect', 'do', 'donate', 'drink',
                         'drive', 'eat', 'emerge', 'enjoy', 'excuse', 'expect', 'feed', 'fight', 'fill', 'flash', 'fly',
                         'forget', 'form', 'get', 'give', 'go', 'graduate', 'grampa', 'grill', 'hang', 'have', 'hear',
                         'heh', 'help', 'hit', 'identify', 'impress', 'influence', 'invite', 'join', 'kid', 'know',
                         'lag', 'leave', 'let', 'like', 'live', 'look', 'love', 'make', 'manage', 'marry', 'mean',
                         'need', 'notice', 'object', 'offer', 'open', 'pass', 'piece', 'pin', 'plate', 'play', 'prefer',
                         'provide', 'quell', 'question', 'realize', 'remember', 'remind', 'remove', 'ride', 'rub',
                         'rush', 'say', 'scold', 'scratch', 'see', 'seem', 'serve', 'show', 'shut', 'sit', 'sleep',
                         'slow', 'sluice', 'sob', 'spray', 'stand', 'stop', 'suck', 'survive', 'swallow', 'take',
                         'talk', 'taste', 'tell', 'think', 'throw', 'toddle', 'tolerate', 'try', 'understand', 'use',
                         'vanish', 'wait', 'want', 'warn', 'watch', 'win']
        self.VERB__VBD = ['added', 'admitted', 'asked', 'ate', 'became', 'bought', 'brought', 'chopped', 'cost',
                          'crammed', 'created', 'did', 'enjoyed', 'expected', 'fired', 'fought', 'found', 'gathered',
                          'gave', 'gone', 'got', 'had', 'happened', 'heard', 'hung', 'kissed', 'learned', 'left',
                          'liked', 'lost', 'loved', 'made', 'managed', 'messed', 'met', 'noticed', 'painted',
                          'performed', 'pulled', 'ran', 'read', 'realized', 'renewed', 'ruined', 'said', 'seemed',
                          'served', 'showed', 'shrunk', 'slang', 'spent', 'started', 'stopped', 'thought', 'thrice',
                          'turned', 'used', 'wanted', 'warned', 'was', 'went', 'were']
        self.VERB__VBG = ['amazing', 'apologizing', 'appetizing', 'arriving', 'attacking', 'badgering', 'being',
                          'bemoaning', 'blowing', 'bouncing', 'calling', 'chasing', 'chewing', 'chuckling', 'closing',
                          'coming', 'connecting', 'couching', 'courting', 'creating', 'displaying', 'doing', 'donating',
                          'driving', 'eating', 'featuring', 'flapping', 'floating', 'flying', 'following', 'forcing',
                          'forming', 'getting', 'going', 'greeting', 'having', 'hitting', 'holding', 'hurting',
                          'ignoring', 'including', 'indicating', 'ing', 'inviting', 'knife', 'laughing', 'leading',
                          'learning', 'leaving', 'looking', 'missing', 'moving', 'observing', 'paying', 'playing',
                          'pointing', 'pushing', 'reading', 'revealing', 'ripping', 'rolling', 'saying', 'scanning',
                          'scooting', 'seeing', 'serving', 'setting', 'shaping', 'sitting', 'sleeping', 'speaking',
                          'spraying', 'spying', 'standing', 'starring', 'starting', 'sticking', 'sucking', 'swilling',
                          'taking', 'talking', 'testing', 'thinking', 'trying', 'uprooting', 'using', 'waiting',
                          'walking', 'watching', 'waving', 'wearing', 'wheeling', 'wrecking', 'writing']
        self.VERB__VBN = ['accompanied', 'animated', 'attached', 'based', 'been', 'brainwashed', 'broken', 'caught',
                          'chanted', 'characterized', 'charmed', 'chopped', 'collected', 'colored', 'come', 'compared',
                          'concerned', 'confused', 'crushed', 'curved', 'depicted', 'directed', 'distorted', 'done',
                          'excised', 'expected', 'exported', 'featured', 'filled', 'forced', 'forged', 'found',
                          'frozen', 'gathered', 'given', 'gone', 'got', 'greeted', 'harmed', 'heard', 'hit', 'invited',
                          'involved', 'known', 'labeled', 'loaded', 'made', 'marked', 'opposed', 'overstimulated',
                          'placed', 'preserved', 'pulled', 'raised', 'raped', 'redistributed', 'replaced', 'reproduced',
                          'required', 'screwed', 'seen', 'shown', 'slammed', 'smashed', 'sprayed', 'supposed', 'timed',
                          'trusted', 'used', 'written']
        self.VERB__VBP = ['ai', 'am', 'apologize', 'appear', 'approach', 'are', 'barbeque', 'begin', 'believe', 'care',
                          'catch', 'chalk', 'come', 'demand', 'descend', 'disappear', 'do', 'dunkin', 'enjoy',
                          'explode', 'feel', 'fight', 'find', 'fly', 'get', 'giggle', 'give', 'go', 'grow', 'guess',
                          'have', 'hear', 'know', 'laugh', 'learn', 'like', 'look', 'love', 'mean', 'need', 'oughta',
                          'perform', 'play', 'remain', 'resemble', 'respect', 'retreat', 'return', 'see', 'seem',
                          'send', 'sigh', 'spit', 'spys', 'stand', 'start', 'suppose', 'take', 'thank', 'think',
                          'thumb', 'understand', 'walk', 'want', 'watch', 'work']
        self.VERB__VBZ = ['agrees', 'allows', 'appears', 'approaches', 'backs', 'beats', 'becomes', 'begins', 'blares',
                          'blinks', 'blows', 'brings', 'builds', 'carries', 'changes', 'chops', 'claps', 'coins',
                          'comes', 'continues', 'covers', 'credits', 'dances', 'depicts', 'disappears', 'dissects',
                          'dissipates', 'does', 'drinks', 'eats', 'falls', 'features', 'fills', 'finds', 'flies',
                          'folds', 'follows', 'forms', 'gets', 'goes', 'growls', 'happens', 'has', 'hears', 'hits',
                          'holds', 'imagines', 'is', 'jumps', 'knocks', 'knows', 'laughs', 'leaves', 'limbos', 'lists',
                          'lives', 'looks', 'loses', 'meets', 'mentions', 'methinks', 'mistakes', 'moves', 'murmurs',
                          'musters', 'needs', 'nudges', 'offers', 'opens', 'overuses', 'pans', 'paraphrases', 'passes',
                          'pets', 'picks', 'places', 'plays', 'points', 'prepares', 'presents', 'presses', 'pulls',
                          'pushes', 'puts', 'quips', 'reaches', 'reacts', 'reappears', 'references', 'remains',
                          'removes', 'rides', 'rises', 'rolls', 'rubs', 'runs', 'sails', 'says', 'seems', 'sees',
                          'sends', 'serves', 'shakes', 'shifts', 'shoots', 'sighs', 'sings', 'slams', 'slaps', 'smacks',
                          'sneaks', 'sounds', 'sparks', 'speaks', 'stares', 'stars', 'starts', 'steps', 'strolls',
                          'struggles', 'swallows', 'swipes', 'switches', 'takes', 'talks', 'tells', 'tests', 'throws',
                          'tilts', 'transcribes', 'troops', 'turns', 'uses', 'walks', 'wants', 'wheels', 'writes']
        self.X__FW = ['av', 'etc', 'la', 'rl']
        self.X__XX = ['th']
        self.professions = ['Accountants', 'Actors', 'Acupuncturists', 'Administrators', 'Advertising executives',
                            'Air traffic controllers', 'Aircraft engineers', 'Anaesthetists', 'Animal breeders',
                            'Anthropologists', 'Antique dealers', 'Archaeologists', 'Architects', 'Archivists',
                            'Aromatherapists', 'Art critics', 'Art dealers', 'Art historians', 'Artists',
                            'Assembly line workers', 'Astrologers', 'Astronomers', 'Au pairs', 'Auctioneers',
                            'Auditors', 'Authors', 'Baggage handlers', 'Bailiffs', 'Bakers', 'Bank clerks',
                            'Bank managers', 'Bar staffs', 'Barbers', 'Barristers', 'Beauty therapists', 'Blacksmiths',
                            'Boat builders', 'Bodyguards', 'Book-keepers', 'Bookmakers', 'Brewers', 'Bricklayers',
                            'Broadcasters', 'Builders', 'Building labourers', 'Bus drivers', 'Business consultants',
                            'Business owners', 'Butchers', 'Butlers', 'Cabin crews', 'Cabinet makers',
                            'Camera operators', 'Car dealers', 'Car wash attendants', 'Care assistants',
                            'Career criminals', 'Careers advisors', 'Caretakers', 'Carpenters', 'Carpet fitters',
                            'Cartoonists', 'Cashiers', 'Casual workers', 'Catering staffs', 'Chauffeurs', 'Chefs',
                            'Chemists', 'Childcare workers', 'Childminders', 'Childrens entertainers', 'Chimney sweeps',
                            'Chiropodists', 'Chiropractors', 'Choreographers', 'Circus workers', 'Civil servants',
                            'Clairvoyants', 'Cleaners', 'Clergymen', 'Clerics', 'Clerical assistants', 'Clockmakers',
                            'Coastguards', 'Comedians', 'Community workers', 'Company directors', 'Composers',
                            'Computer analysts', 'Computer engineers', 'Computer programmers', 'Conservationists',
                            'Construction workers', 'Cooks', 'Coroners', 'Costume designers', 'Counsellors',
                            'Councillors', 'Couriers', 'Craftspeople', 'Crane drivers', 'Crematorium workers',
                            'Croupiers', 'Crown prosecutors', 'Curators', 'Customs officers', 'Dancers',
                            'Data processors', 'Debt collectors', 'Decorators', 'Delivery drivers', 'Dental hygienists',
                            'Dental nurses', 'Dentists', 'Designers', 'Dieticians', 'Diplomats', 'Directors',
                            'Disc jockeys', 'Divers', 'Doctors', 'Domestic staffs', 'Doormen', 'Dressmakers',
                            'Driving instructors', 'Drug dealers', 'Economists', 'Editors', 'Electricians', 'Engineers',
                            'Estate agents', 'Events organisers', 'Factory workers', 'Fairground workers', 'Farmers',
                            'Farm workers', 'Fashion designers', 'Film directors', 'Financial advisors', 'Firefighters',
                            'Fisherman/women', 'Fitness instructors', 'Flower arrangers', 'Flying instructors',
                            'Footballers', 'Fork-lift drivers', 'Foster parents', 'Fundraisers', 'Funeral directors',
                            'Gamekeepers', 'Garden designers', 'Gardeners', 'Gas fitters', 'Genealogists',
                            'Grave diggers', 'Grooms', 'Hairdressers', 'Handymen', 'Healthcare assistants',
                            'Health visitors', 'Heating engineers', 'Herbalists', 'Historians', 'Homeopaths',
                            'Homemakers', 'Home-workers', 'Horticulturalists', 'Housekeepers', 'Hypnotherapists',
                            'Illustrators', 'Immigration officers', 'Independent meanss', 'Insurance consultants',
                            'Interior designers', 'Interpreters', 'Inventors', 'IT consultants', 'Jewellery makers',
                            'Jockeys', 'Journalists', 'Judges', 'Kennel workers', 'Laboratory technicians', 'Labourers',
                            'Landowners', 'Landscape gardeners', 'Lap dancers', 'Lawyers', 'Leaflet distributors',
                            'Lecturers', 'Legal secretarys', 'Librarians', 'Lifeguards', 'Lift engineers',
                            'Lighthouse keepers', 'Literary agents', 'Local govt workers', 'Lock keepers', 'Locksmiths',
                            'Lorry drivers', 'Machinists', 'Magicians', 'Magistrates', 'Make-up artists',
                            'Management consultants', 'Managing directors', 'Manicurists', 'Market traders',
                            'Marketing directors', 'Massage therapists', 'Mathematicians', 'Medical students',
                            'Merchant navy personnels', 'Meteorologists', 'Meter readers', 'Midwives', 'Miners',
                            'Ministers', 'Missionarys', 'Models', 'Moneylenders', 'Morticians', 'Musicians', 'Nuns',
                            'Nurses', 'Occupational therapists', 'Oil rig crews', 'Opticians', 'Osteopaths',
                            'Paramedics', 'Park-keepers', 'Park rangers', 'Party planners', 'Pathologists',
                            'Pawnbrokers', 'Pest controllers', 'Pharmacists', 'Photographers', 'Physiotherapists',
                            'Pickpockets', 'Picture framers', 'Pilots', 'Plasterers', 'Plumbers', 'Police officers',
                            'Politicians', 'Pop stars', 'Porters', 'Postal delivery workers', 'Preachers', 'Priests',
                            'Printers', 'Prison officers', 'Private investigators', 'Probation officers', 'Producers',
                            'Professors', 'Property developers', 'Prostitutes', 'Psychiatrists', 'Psychologists',
                            'Publicans', 'Publishers', 'Racing drivers', 'Radio presenters', 'Receptionists',
                            'Refuse collectors', 'Reporters', 'Researchers', 'Retireds', 'Road sweepers', 'Roofers',
                            'Sailors', 'Salespeople', 'Scaffolders', 'School crossing wardens',
                            'School meals supervisors', 'Scientists', 'Sculptors', 'Secretarys', 'Security guards',
                            'Ship builders', 'Singers', 'Shoemakers', 'Shop assistants', 'Social workers',
                            'Software consultants', 'Soldiers', 'Solicitors', 'Song writers', 'Special constables',
                            'Speech therapists', 'Sports coaches', 'Sportspeople', 'Stockbrokers',
                            'Street entertainers', 'Students', 'Surgeons', 'Surveyors', 'Tailors', 'Tarot Readers',
                            'Tattooists', 'Tax inspectors', 'Taxi drivers', 'Teachers', 'Teaching assistants',
                            'Telephonists', 'Telesales people', 'Television presenters', 'Toilet attendants',
                            'Tour guides', 'Traffic wardens', 'Train drivers', 'Travel agents', 'Typists',
                            'Undertakers', 'Veterinary surgeons', 'Waiting staffs', 'Window cleaners']

        self._type_map = dict(adjective=self.ADJ__JJ,
                              adjective_er=self.ADJ__JJR,
                              gerund=self.VERB__VBG,
                              past_participle=self.VERB__VBN,
                              noun=self.NOUN__NN + self.PROPN__NNPS,
                              plural_noun=self.NOUN__NNS,
                              plural_profession=self.professions)

    def by_word_type(self, word_type):
        return self._type_map[word_type]


class _MadLibs(Routine):
    def __init__(self):
        super().__init__('madlib', as_mp3=True)
        self._mad_lib = """
            When you hear the words Artificial Intelligence you may
            think of scary things like <plural_noun> , telemarketer
            bots, and <plural_noun> taking over the world. AI shouldn't
            be scary. At its core it is simply changing input Eh into
            output B. In digital advertising the input is almost always
            <noun>. The output could be the sale of a  <noun>, a consumer
            <gerund> your store, or a show being watched. Millions of
            queries per second are processed resulting in  <adjective>
            amounts of data. The growing detail and scale of this data
            presents great opportunity for <plural_profession>, who can
            harness it effectively to achieve their desired  <plural_noun>.
            AI is trained to find pockets of performance in these massive
            amounts of data, like finding a  <noun> in a <noun>. One
            of the greatest fears surrounding AI is that humans will
            be  <past_participle>. We believe there is a harmony between
            humans and our  <adjective> technology, Copilot. Copilot
            uses hundreds of thousands of machine learning models to
            drive smarter,  <adjective_er> optimization. The human touch
            and custom approach for each  <noun> is crucial. Don't be
            afraid of AI, let it help you reach your  <adjective> goals.
        """
        self.mad_lib, self._options = self._init_obj()

    def _init_obj(self):
        import re
        pattern = re.compile('<.*?>')
        mad_lib = re.sub(r'\s+', ' ', self._mad_lib).strip()
        sentences = (s for s in re.split(pattern, mad_lib) if s)
        word_types = (w.lstrip('<').rstrip('>') for w in re.findall(pattern, mad_lib))
        options = list(map(mad_libs_words.by_word_type, word_types))
        words = (choice(list(o)) for o in options)
        start_with_words = bool(re.match(pattern, mad_lib))
        first, second = sentences, words
        if start_with_words:
            first, second = second, first

        return ' '.join(interleave_longest(first, second)), options

    async def run(self):
        await self._generate()
        await self.mad_lib


mad_libs_words = _MadLibsWords()
mad_libs = _MadLibs()


async def explore():
    for t in mad_libs_words:
        print(80 * '=')
        # with suppress(Exception):
        for term in t.split('__'):
            term = term.replace('dollarsign', '$')
            print(term, spacy.explain(term))
        vals = list(mad_libs_words[t])
        print([choice(vals) for _ in range(7)])
        print(80 * '=')
        # for _ in range(3):
        #     await mad_libs[t]
        print()


def change_plurality():
    import inflect
    p = inflect.engine()
    print(list(map(p.plural_noun, mad_libs_words.professions)))


def __main():
    # mad_libs.generate()
    print(first(mad_libs.mad_lib.values()))
    asyncio.run(mad_libs.run())
    pass
    # print(mad_libs.professions)
    # mad_libs_words.generate('professions')
    # change_plurality()
    # asyncio.run(explore())
    # for t in mad_libs:
    #     for term in t.split('__'):
    #         term = term.replace('dollarsign', '$')
    #         print(term, spacy.explain(term))
    #     print()


if __name__ == '__main__':
    __main()
