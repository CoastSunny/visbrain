"""Colorbar management for the Brain module."""
import logging

from ...visuals import CbarQt, CbarObjetcs, CbarBase

logger = logging.getLogger('visbrain')

__all__ = ['BrainCbar']


class BrainCbar(object):
    """Create the colorbar, the objects and updating functions."""

    def __init__(self, camera):
        """Init."""
        # ------------------- CBOBJS -------------------
        # Create the cbar objects manager :
        self.cbobjs = CbarObjetcs()

        # ------------------- CBARBASE -------------------
        # ________ BRAIN ________
        cbproj = CbarBase(**self.atlas.to_dict())
        self.cbobjs.add_object('Brain', cbproj)
        obj = self.cbobjs._objs['Brain']
        obj._fcn = self._fcn_link_brain
        obj._minmaxfcn = self._fcn_minmax_brain

        # ________ Connectivity ________
        if self.connect.name is not None:
            for k in self.connect:
                cbconnect = CbarBase(**self.connect[k.name].to_dict())
                self.cbobjs.add_object(k.name, cbconnect)
                obj = self.cbobjs._objs[k.name]
                obj._fcn = self._fcn_link_connect(k.name)
                obj._minmaxfcn = self._fcn_minmax_connect(k.name)

        # ________ Pictures ________
        if self.pic.name is not None:
            for k in self.pic:
                cbpic = CbarBase(**self.pic[k.name].to_dict())
                self.cbobjs.add_object(k.name, cbpic)
                obj = self.cbobjs._objs[k.name]
                obj._fcn = self._fcn_link_pic(k.name)
                obj._minmaxfcn = self._fcn_minmax_pic(k.name)

        # ________ Default ________
        if all([k.name is None for k in (self.sources, self.pic,
                                         self.connect)]):
            cbproj = CbarBase()
            self.cbobjs.add_object('default', cbproj)

        # ------------------- CBQT -------------------
        # Add colorbar and interactions :
        self.cbqt = CbarQt(self._cbarWidget, self.cbpanel, self.cbobjs)
        is_cbqt = bool(self.cbqt)
        if is_cbqt:
            self.cbqt.select(0)
            self.cbqt._fcn_change_object()
        self.menuDispCbar.setEnabled(is_cbqt)

        # Add the camera to the colorbar :
        self.cbqt.add_camera(camera)

    ###########################################################################
    #                              BRAIN
    ###########################################################################
    def _fcn_link_brain(self):
        """Executed function when projection need updates."""
        kwargs = self.cbqt.cbobjs._objs['Brain'].to_kwargs(True)
        self.atlas.update_from_dict(kwargs)
        self.atlas._update_cbar()

    def _fcn_minmax_brain(self):
        """Executed function for autoscale projections."""
        self.cbqt.cbobjs._objs['Brain']._clim = self.atlas._minmax
        self.atlas._clim = self.atlas._minmax
        self.atlas._update_cbar()

    ###########################################################################
    #                              CONNECTIVITY
    ###########################################################################
    def _fcn_link_connect(self, name):
        """Executed function when connectivity need updates."""
        def _get_connect_fcn():
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs(True)
            self.connect[name].update_from_dict(kwargs)
            self.connect[name]._build_line()
        return _get_connect_fcn

    def _fcn_minmax_connect(self, name):
        """Executed function for autoscale connectivity."""
        def _get_minmax_connect_fcn():
            self.cbqt.cbobjs._objs[name]._clim = self.connect[name]._minmax
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs(True)
            self.connect[name].update_from_dict(kwargs)
            self.connect[name]._build_line()
        return _get_minmax_connect_fcn

    ###########################################################################
    #                              PICTURES
    ###########################################################################
    def _fcn_link_pic(self, name):
        """Executed function when pictures need updates."""
        def _get_pic_fcn():
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs()
            self.pic[name].update_from_dict(kwargs)
            self.pic[name]._pic.set_data(**kwargs)
        return _get_pic_fcn

    def _fcn_minmax_pic(self, name):
        """Executed function for autoscale pictures."""
        def _get_minmax_pic_fcn():
            self.cbqt.cbobjs._objs[name]._clim = self.pic[name]._minmax
            kwargs = self.cbqt.cbobjs._objs[name].to_kwargs()
            self.pic[name].update_from_dict(kwargs)
            self.pic[name]._pic.set_data(**kwargs)
        return _get_minmax_pic_fcn