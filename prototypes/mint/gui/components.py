import logging
from PySide.QtCore import *
from PySide.QtGui import *
from misc import Console
from mint.utils import each

log = logging.getLogger('component')

def create(model):
    try:
        role = type(model).role
    except AttributeError:
        log.warning('{} got no role'.format(model))
    else:
        if role in ('Host', 'Hub', 'Switch', 'Router', 'Link'):
            return eval(role)(model)
    return None

class Model(object):

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(Model, self).__init__(*args, **kwargs)
        self.console = Console(model)
        self.setToolTip(str(self.model))

    @property
    def console_offset(self):
        return self.console.scenePos() - self.scenePos()

    @property
    def console_size(self):
        return self.console.size()

    def mouseDoubleClickEvent(self, ev):
        self.console.enabled = not self.console.enabled

    def toggle(self, what):
        if what == 'console enabled':
            self.console.enabled = not self.console.enabled
        elif what == 'console visible':
            self.console.visible = not self.console.visible
        elif what == 'console frame':
            self.console.has_frame = not self.console.has_frame

    def refresh(self):
        self.console.refresh()

    def itemChange(self, change, val):
        if change == QGraphicsItem.ItemPositionChange:
            val = super(Model, self).itemChange(change, val)
            offset = val - self.pos()
            self.console.moveBy(offset.x(), offset.y())
            return val
        return super(Model, self).itemChange(change, val)

class Device(Model, QGraphicsPixmapItem):

    def __init__(self, model):
        super(Device, self).__init__(model, self.pic)
        self.links = []
        self.setOffset(-self.pixmap().width() / 2.0,
                       -self.pixmap().height() / 2.0)
        self.setFlags(self.ItemIsSelectable |
                      self.ItemIsMovable |
                      self.ItemSendsGeometryChanges)

    @property
    def pic(self):
        cls = type(self)
        while True:
            try:
                return cls._pic
            except AttributeError:
                pics = QApplication.instance().resources['pics']
                cls._pic = pics.get(cls.__name__, pics['default'])

    def boundingRect(self):
        return super(Device, self).boundingRect().adjusted(0, 0, 0, 20)

    def paint(self, p, *args):
        super(Device, self).paint(p, *args)
        p.drawText(self.boundingRect(), Qt.AlignBottom | Qt.AlignHCenter,
                   str(self.model))

    def itemChange(self, change, val):
        if change == self.ItemPositionHasChanged:
            each(self.links).track_device()
        return super(Device, self).itemChange(change, val)

class Host(Device):

    def __init__(self, model):
        super(Host, self).__init__(model)

class Switch(Device): pass

class Router(Device): pass

class Link(Model, QGraphicsLineItem):

    def __init__(self, model):
        super(Link, self).__init__(model)
        self._devices = None
        pen = self.pen()
        pen.setWidth(2)
        self.setPen(pen)

    @property
    def console_offset(self):
        return self.console.scenePos() - self.line().pointAt(0.5)

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, val):
        self._devices = val
        each(self._devices).links.append(self)
        self.track_device()

    def track_device(self):
        old_line = self.line()
        new_line = QLineF(*each(self.devices).scenePos())
        old_mid_pt = old_line.pointAt(0.5)
        new_mid_pt = new_line.pointAt(0.5)
        offset = new_mid_pt - old_mid_pt
        self.console.moveBy(offset.x(), offset.y())
        self.setLine(new_line)

    def sending_progress(self, device):
        entity = device.model
        link = self.model
        tip = link[entity]
        sending = entity.sending(at=tip)
        if not sending:
            return 0
        return entity.sent(at=tip) / float(sending + link.latency)

    def paint(self, p, *args):
        super(Link, self).paint(p, *args)
        pg0 = self.sending_progress(self.devices[0])
        pg1 = self.sending_progress(self.devices[1])
        line = self.line()
        #print '!!!', pg0, pg1
        line2 = QLineF(line.p2(), line.p1())
        #print line.length(), line2.length()
        if pg0:
            self.draw_arrow(p, pg0, line)
        if pg1:
            self.draw_arrow(p, pg1, QLineF(line.p2(), line.p1()))

    def draw_arrow(self, p, ratio, line, length=10):
        line = QLineF(line)
        line.setP2(line.pointAt(1 - length / line.length()))
        pt = QPointF(line.length() * ratio, -10)
        p.save()
        p.translate(line.p1())
        p.rotate(-line.angle())
        pixmap = QApplication.instance().resources['pics']['frame']
        p.drawPixmap(pt - QPointF(pixmap.width() / 2.0, pixmap.height() / 2.0), pixmap)
        p.restore()
