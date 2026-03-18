"""
A Singleton Sprite Manager class
Author: Liz Matthews, 7/21/2023

Provides on-demand loading of images for a pygame program.
Will load entire sprite sheets if given an offset.

"""

from pygame import image, Surface, Rect, SRCALPHA
from pygame.transform import scale_by
from os.path import join
from vector import vec, pyVec

class SpriteManager(object):
    """A singleton factory class to create and store sprites on demand.
    Do not directly instantiate this class! Use SpriteManager.getInstance()."""
    
    # The singleton instance variable
    _INSTANCE = None
    
    @classmethod
    def getInstance(cls):
        """Used to obtain the singleton instance"""
        if cls._INSTANCE == None:
            cls._INSTANCE = cls()
        
        return cls._INSTANCE
    
    # Folder in which images are stored
    _IMAGE_FOLDER = "images"
    
    ### PROPERTIES TO CHANGE TO ADD NEW IMAGES ###
    
    # Static information about the sprite sizes of particular image sheets.
    _SPRITE_SIZES = {
        "Kirby.png": vec(16, 16),
        "rose.png": vec(34,68)
    }
    
    # A default sprite size
    _DEFAULT_SPRITE = vec(32, 32)
    
    # If images need to be rescaled
    _SCALES = {
        "background.png": 0.35
        # Can also be two dimensional, ex: vec(2, 3)
    }
    
    # A list of images that require to be loaded with transparency
    _TRANSPARENCY = [
        "rose.png",
        "Conveyor Belts sprite sheet.png",
        "Character Sprites/CharacterModel/Character Model.png",
        "Character Sprites/CharacterModel/Shadow.png",
        "Character Sprites/Suit.png",
        "freight/Freight-1.png",
        "freight/Freight-2.png",
        "freight/Freight-3.png",
        "freight/Freight-5.png",
        "freight/Freight-6.png",
        "freight/Freight-7.png",
        "freight/Freight-8.png",
        "freight/Freight-9.png",
        "freight/Freight-10.png",
        "Office-Furniture-Pixel-Art/Big-Office-Printer.png",
        "Office-Furniture-Pixel-Art/Big-Round-Table.png",
        "Office-Furniture-Pixel-Art/Bookshelf.png",
        "Office-Furniture-Pixel-Art/Boss-Desk.png",
        "Office-Furniture-Pixel-Art/Chair.png",
        "Office-Furniture-Pixel-Art/Desk.png",
        "Office-Furniture-Pixel-Art/Filing-Cabinet-Small.png",
        "Office-Furniture-Pixel-Art/Filing-Cabinet-Tall.png",
        "Office-Furniture-Pixel-Art/Folders-2.png",
        "Office-Furniture-Pixel-Art/Folders.png",
        "Office-Furniture-Pixel-Art/Mirror.png",
        "Office-Furniture-Pixel-Art/Papers.png",
        "Office-Furniture-Pixel-Art/Printer-Furniture.png",
        "Office-Furniture-Pixel-Art/Printer.png",
        "Office-Furniture-Pixel-Art/Small-Plant.png",
        "Office-Furniture-Pixel-Art/Small-Sofa.png",
        "Office-Furniture-Pixel-Art/Small-Table.png",
        "Office-Furniture-Pixel-Art/Tall-Bookshelf.png",
        "Office-Furniture-Pixel-Art/Toilet-Closed.png",
        "Office-Furniture-Pixel-Art/Toilet-Open.png",
        "Office-Furniture-Pixel-Art/Vending-Machine.png",
        "Office-Furniture-Pixel-Art/Wall-Clock.png",
        "Office-Furniture-Pixel-Art/Wall-Graph.png",
        "Office-Furniture-Pixel-Art/Wall-Note-2.png",
        "Office-Furniture-Pixel-Art/Wall-Note.png",
        "Office-Furniture-Pixel-Art/Wall-Shelf.png",
        "Office-Furniture-Pixel-Art/Water-Dispenser.png",
        "Office-Furniture-Pixel-Art/WC-Paper.png",
        "Office-Furniture-Pixel-Art/WC-Sink.png",
        "Office-Furniture-Pixel-Art/Wide-Filing-Cabinet.png",
        "2D_TOPDOWN_PIXELART_CARS.png",
        "BOX TRUCK TOPDOWN/Blue/MOVE/SOUTH/SEPARATED/Blue_BOXTRUCK_CLEAN_SOUTH_000.png",
        "BOX TRUCK TOPDOWN/Red/MOVE/SOUTH/SEPARATED/Red_BOXTRUCK_CLEAN_SOUTH_000.png",
        "VAN TOP DOWN/White/MOVE/SOUTH/SEPARATED/White_VAN_CLEAN_SOUTH_000.png",
        "VAN TOP DOWN/Yellow/MOVE/SOUTH/SEPARATED/Yellow_VAN_CLEAN_SOUTH_000.png",
        "kenney_car-kit_3.0/Previews/box.png",
        "kenney_car-kit_3.0/Previews/cone.png",
        "kenney_car-kit_3.0/Previews/delivery.png",
        "kenney_car-kit_3.0/Previews/delivery-flat.png",
        "kenney_car-kit_3.0/Previews/garbage-truck.png",
        "kenney_car-kit_3.0/Previews/truck.png",
        "kenney_car-kit_3.0/Previews/truck-flat.png",
        "kenney_car-kit_3.0/Previews/van.png"
    ]
    
    # A list of images that require to be loaded with a color key
    _COLOR_KEY = ["Kirby.png"]
    
    def __init__(self):
        """Creation of the SpriteManager, sets up storage for surface.
        Can only be called once."""
        if self._INSTANCE != None:
            raise RuntimeError("Cannot create more than one instance of the SpriteManager.")
        
        # Stores the surfaces indexed based on file name
        self._surfaces = {}

        self._fullSurfaces = {}
    
    def __getitem__(self, key):
        return self.getSprite(key)
    
    def getSize(self, fileName):
        spriteSize = self._SPRITE_SIZES.get(fileName,
                                            self._DEFAULT_SPRITE)

        scale = self._SCALES.get(fileName, 
                                 1)
        return pyVec(spriteSize * scale)
    
    def getSprite(self, fileName, offset=None):
        # If this sprite has not already been loaded, load the image from memory
        if fileName not in self._surfaces.keys():
            self._loadImage(fileName, offset)
          
        
        # If the offset is arbitrary, flyweight load the rect offset
        if type(offset) == Rect or (type(offset) in [list, tuple] \
                                    and len(offset) == 4):
            if type(offset) != Rect:
                offset = Rect(offset)
                
            if tuple(offset) not in self._surfaces[fileName]:
                self._surfaces[fileName][tuple(offset)] = self._loadRect(fileName,
                                                               self._surfaces[fileName]["full"],
                                                               offset)
            return self._surfaces[fileName][tuple(offset)]
        
        # If this is an image sheet, return the correctly offset sub surface
        elif type(offset) in [list, tuple] and len(offset) == 2:
            return self._surfaces[fileName][offset[1]][offset[0]] 
        
        # Otherwise, return the sheet created
        return self._surfaces[fileName]
 
    def _loadImage(self, fileName, offset=None):
        # Load the full image      
        fullImage = self._loadFull(fileName)
        
        fullImage = scale_by(fullImage,
                             self._SCALES.get(fileName,
                             1))
        
        
        # If the image to be loaded is an image sheet, split it up based on the sprite size
        if type(offset) in [list, tuple] and len(offset) == 2:
            self._loadSpriteSheet(fileName, fullImage)
        
        # If the image is an arbitrary offset set up a dictionary and store the full image
        elif type(offset) == Rect or (type(offset) in [list, tuple] \
                                      and len(offset) == 4):
            self._surfaces[fileName] = {}
            self._surfaces[fileName]["full"] = fullImage
           
        # If there is no offset store the entire image
        elif offset == None:
            self._surfaces[fileName] = fullImage
           
            # If we need to set the color key
            self._applyColorKey(fileName, fullImage)
        
        else:
            raise TypeError(f"Offset must be of type Rect, List, Tuple, or None. Length of List/Tuple must be 2 for spriteSheet offset or 4 for arbitrary rect.")
 
    def _loadFull(self, fileName):
        fullImage = image.load(join(self._IMAGE_FOLDER, fileName))
       
        # Detect if a transparency is needed
        fullImage = self._applyTransparency(fileName, fullImage)
        
        return fullImage
 
    def _loadRect(self, fileName, fullImage, rect):
        sprite = self._applyTransparency(fileName, rect=rect)
           
        sprite.blit(fullImage, (0,0), rect)
        
        self._applyColorKey(fileName, sprite)
        
        return sprite
    
    def _loadSpriteSheet(self, fileName, fullImage):
        self._surfaces[fileName] = []
        
        # Try to get the sprite size, use the default size if it is not stored
        spriteSize = self.getSize(fileName)
        
        # See how big the sprite sheet is
        sheetDimensions = fullImage.get_size()
        
        # Iterate over the entire sheet, increment by the sprite size
        for y in range(0, sheetDimensions[1], spriteSize[1]):
            self._surfaces[fileName].append([])
            for x in range(0, sheetDimensions[0], spriteSize[0]):
                # Add the sprite to the end of the current row
                self._surfaces[fileName][-1].append(self._loadRect(fileName,
                                                         fullImage,
                                                         Rect((x,y),
                                                               spriteSize)))
         
               
    def _applyColorKey(self, fileName, surface):
        if fileName in self._COLOR_KEY:
            surface.set_colorkey(surface.get_at((0,0)))

    def _applyTransparency(self, fileName, img=None, rect=None):
        if fileName in self._TRANSPARENCY:
            if img:
                returnImage = img.convert_alpha()
            else:
                returnImage = Surface(rect.size, SRCALPHA, 32)
        else:
            if img:
                returnImage = img.convert()
            else:
                returnImage = Surface(rect.size)
                
        return returnImage
