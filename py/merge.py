def getRectDis(r1, r2):
    left = r1[0] < r2[0] and r1[0] or r2[0]
    top = r1[1] < r2[1] and r1[1] or r2[1]
    right = r1[0] + r1[2] > r2[0] + r2[2] and r1[0] + r1[2] or r2[0] + r2[2]
    bottom = r1[1] + r1[3] > r2[1] + r2[3] and r1[1] + r1[3] or r2[1] + r2[3]
    dw = max(right - left - r1[2] - r2[2], 0)
    dh = max(bottom - top - r1[3] - r2[3], 0)
    return dw + dh


def mergeRect(r1, r2):
    left = r1[0] < r2[0] and r1[0] or r2[0]
    top = r1[1] < r2[1] and r1[1] or r2[1]
    right = r1[0] + r1[2] > r2[0] + r2[2] and r1[0] + r1[2] or r2[0] + r2[2]
    bottom = r1[1] + r1[3] > r2[1] + r2[3] and r1[1] + r1[3] or r2[1] + r2[3]
    return [left, top, right - left, bottom - top]


def checkMergeRects(sprite, dis=2):
    rects = sprite.sub_list
    names = sprite.name_list
    size = len(rects)
    for i in range(size):
        for j in range(i):
            if rects[j] is None:
                continue
            rect1 = rects[i]
            rect2 = rects[j]
            if getRectDis(rect1, rect2) < dis:
                rects[j] = None
                names[j] = None
                rects[i] = mergeRect(rect1, rect2)
        pass
    sprite.sub_list = list(filter(None, rects))
    sprite.name_list = list(filter(None, names))
