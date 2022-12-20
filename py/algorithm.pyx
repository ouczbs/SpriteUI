import numpy as np
def seedsAll_yield(sprite):
    cdef int h , w , i , j
    h,w = sprite.h , sprite.w
    cdef long long[:,:] mask = sprite.mask
    cdef int class_k = 1
    for i in range(h):
        for j in range(w):
            if mask[i,j] != 0:
                continue
            class_k = class_k + 1
            yield i ,j , class_k
    pass
connects = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1],[-1, 0]]
cdef class RegionRectGrow():
    cdef int top,left,right,bottom
    cdef inline init_rect(self, int y, int x):
        self.left = x
        self.right = x
        self.top = y
        self.bottom = y
    cdef inline add_rect(self, sprite,int class_k):
        cdef int w,h
        w,h = self.right - self.left + 1, self.bottom - self.top + 1
        if w * h > 32:
            sprite.add_rect([self.left , self.top , w , h])
    def run(self, sprite, int y ,int x ,int class_k):
        self.init_rect(y , x)
        seed_list = [[y, x]]
        self.setMask(sprite.mask, y , x , class_k)
        while (len(seed_list) > 0):
            self.region_grow(seed_list, sprite, class_k)
            self.expand_rect(seed_list,sprite.mask , class_k)
        self.add_rect(sprite , class_k)
    cdef inline region_grow(self ,seed_list, sprite ,int class_k):
        cdef int height,width
        cdef int ty,tx , cy , cx , ny,nx
        cdef int value
        cdef long long[:,:] mask
        height,width = sprite.h , sprite.w
        pixmap,mask = sprite.pixmap,sprite.mask
        while (len(seed_list) > 0):
            ty,tx = seed_list.pop()
            for i in range(8):
                cy,cx = connects[i]
                ny,nx = ty + cy,tx + cx
                if nx < 0 or ny < 0 or ny >= height or nx >= width:
                    continue
                value = mask[ny, nx]
                if value == class_k or value == 1:
                    continue
                self.setMask(mask, ny , nx , class_k)
                seed_list.append([ny , nx])
        pass

    cdef inline setMask(self,long long[:,:] mask,int y ,int x,int class_k):
        if self.left > x:
            self.left = x
        elif self.right < x:
            self.right = x
        if self.top > y:
            self.top = y
        elif self.bottom < y:
            self.bottom = y
        mask[y,x] = class_k
    cdef inline expand_rect(self,seed_list ,long long[:,:] mask ,int class_k):
        cdef int i,j,value
        for i in range(self.top , self.bottom + 1):
            for j in range(self.left , self.right + 1):
                value = mask[i, j]
                if value == class_k or value == 1:
                    continue
                self.setMask(mask ,i , j , class_k)
                seed_list.append([i , j])
        pass
def markMaskBg(sprite,int k ,int mi ,int ma):
    pixmap = sprite.pixmap
    mask = sprite.mask
    bool_mask = (pixmap[:,:,k] < ma) & (pixmap[:,:,k] > mi)
    mask[bool_mask] = 1
def makeRegionRectGrow():
    return RegionRectGrow()
def run_all(algorithm ,sprite , seeds_generator):
    cdef int i,j, k
    for i,j,k in seeds_generator:
        algorithm.run(sprite , i , j , k)
def run_step(algorithm ,sprite ,int i ,int j,int k):
    algorithm.run(sprite , i, j , k)