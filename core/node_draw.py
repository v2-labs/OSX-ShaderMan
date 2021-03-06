""" Here we're painting the bricks.

Note we're using wxPython facilities for actual painting, and then just mapping the corresponding bitmap to the OpenGL texture.

"""

import wx
from core import node
from core.panel import *
from core.utils import *
from core.shared import *

headerh = 24
dh = 4
fontsize = 0
color = None
lcolor = None
hcolor = None

# should be Factory/function ?
TypeColors = { "float" : wx.RED, "color" : wx.GREEN, "string" : wx.BLUE, "variant" : wx.BLACK, "point" : wx.CYAN, "vector" : wx.CYAN, "normal" : wx.CYAN }

def InitNodeDraw():
	global fontsize
	global color
	global lcolor
	global hcolor
	if wx.Platform == "__WXMAC__":
		fontsize = float(settings.get("fontsize", 12))
		color = wx.Colour(220, 220, 220)
	else:
		fontsize = float(settings.get("fontsize", 10))
		color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
		
	color2 = settings.get("bgcolor", None)
	if color2 is not None:
		color2 = [int(c) for c in color2.split(",")]
		color = wx.Colour(color2[0], color2[1], color2[2])

	lhsv = RGBtoHSV(color.Get())
	lhsv[2] -= 20
	lrgb = HSVtoRGB(lhsv)
	
	lrgb = [max(x, 0) for x in lrgb]
	
	lcolor = wx.Colour(lrgb[0], lrgb[1], lrgb[2])

	hhsv = RGBtoHSV(color.Get())
	hhsv[2] += 9
	hrgb = HSVtoRGB(hhsv)
	
	hrgb = [min(x, 255) for x in hrgb]
	
	hcolor = wx.Colour(hrgb[0], hrgb[1], hrgb[2])

def SunkenLine(left, top, width, hcolor, lcolor, dc):
	dc.SetPen(wx.Pen(lcolor, 1))
	dc.DrawLine(left, top, left+width+1, top)
	dc.SetPen(wx.Pen(hcolor, 1))
	dc.DrawLine(left, top+1, left+width+1, top+1)
	
def CalcGroupSize(group, dc):
	font = wx.Font(fontsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
	dc.SetFont(font)
	
	headerh = dc.GetCharHeight()+6
	width = dc.GetFullTextExtent("group%s" % group.id)[0]
	hh = dc.GetFullTextExtent("group%s" % group.id)[1]
	dh = (headerh-hh)/2
	
	w1 = width + 2*headerh + 4*dh
	
	return width, headerh, dh, w1

def CalcMinMaxSize(node, dc):
	itemcount = max(len(node.in_params), len(node.out_params))
	itemcount += 1 # header
	
	font = wx.Font(fontsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
	dc.SetFont(font)
	
	headerh = dc.GetCharHeight()+6
	dh = (headerh-dc.GetFullTextExtent(node.name)[1])/2
	
	if node.panel.showParameters and not node.panel.iconicMode:
		height = headerh * itemcount
	else:
		height = headerh
	
	if node.panel.iconicMode:
		width = headerh
	else:
		width = headerh*2
	
	width1 = 0
	if node.panel.showParameters and not node.panel.iconicMode:
		extents = [ dc.GetFullTextExtent(str(inp["name"])) for inp in node.in_params ]
		widths = [ extent[0] for extent in extents ]
		if len(widths)>0:
			width1 = max(widths)

	width2 = 0
	if node.panel.showParameters and not node.panel.iconicMode:
		extents = [ dc.GetFullTextExtent(str(inp["name"])) for inp in node.out_params ]
		widths = [ extent[0] for extent in extents ]
		if len(widths)>0:
			width2 = max(widths)
	
	if not node.panel.iconicMode:
		width += max(width1+width2+headerh*2, dc.GetFullTextExtent(str(node.name))[0])
	
	return width, height, headerh, dh, width1, width2
	
def CalcArrowPosition(index, dc, node=None):
	font = wx.Font(fontsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
	dc.SetFont(font)
	
	headerh = dc.GetCharHeight()+6
	result = headerh * (index+1) + headerh/2 # because of header; beware of the preview placement!!!
	if node != None:
		if not node.panel.showParameters or node.panel.iconicMode:
			result = headerh/2
	return result

def IsArrowStart(anode, dc, x, y):
	width, height, headerh, dh, col1, col2 = CalcMinMaxSize(anode, dc)
	ahh = headerh-dh*2
	
	xx = x-anode.panel.x
	yy = y-anode.panel.y
		
	for i in range(1, len(anode.out_params)+1):
		if (xx in range(col1+headerh*2+2, width)) and (yy in range(i*headerh, (i+1)*headerh)):
			return i
				
	return -1
	
def IsArrowEnd(anode, dc, x, y):
	width, height, headerh, dh, col1, col2 = CalcMinMaxSize(anode, dc)
	ahh = headerh-dh*2
	
	xx = x-anode.panel.x
	yy = y-anode.panel.y
		
	for i in range(0, len(anode.in_params)+1):
		if (xx in range(0, col1+headerh*2)) and (yy in range(i*headerh, (i+1)*headerh)):
			return i	
				
	return -1
	
def PaintGroup(group, dc):
	mdc = wx.MemoryDC()
	font = wx.Font(fontsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
	mdc.SetFont(font)
	
	width, headerh, dh, w1 = CalcGroupSize(group, dc) # mdc?
	
	bmp = wx.EmptyBitmap(width, headerh)
	mdc.SelectObject(bmp)
	
	# glColor4f( 36/255.0, 206/255.0, 36/255.0, 0.5 )
	group_color = wx.Colour(161, 223, 149)
	
	mdc.SetBrush(wx.Brush(group_color))
	mdc.SetPen(wx.Pen(group_color, 1, wx.TRANSPARENT))
	mdc.DrawRectangle(0, 0, width, headerh)
	
	mdc.DrawText("group%s" % group.id, 0, dh)
	
	del mdc
	if __name__ == '__main__':
		dc.DrawBitmap(bmp, top, left)
	
	return bmp

def PaintForm(anode, left, top, dc):
	
        mdc = wx.MemoryDC()
	font = wx.Font(fontsize, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
	mdc.SetFont(font)
	
	width, height, headerh, dh, col1, col2 = CalcMinMaxSize(anode, dc) # mdc?
	
	bmp = wx.EmptyBitmap(width, height)
	mdc.SelectObject(bmp)
	
	mdc.SetBrush(wx.Brush(color))

	# bg
	mdc.SetPen(wx.Pen(color, 1, wx.TRANSPARENT))
	mdc.DrawRectangle(0, 0, width, height)
	
	# header bg
	mdc.SetBrush(wx.Brush(lcolor))
	mdc.DrawRectangle(0, 0, width+1, headerh)
	mdc.SetBrush(wx.Brush(color))
	
	# header separator
	SunkenLine(0, headerh, width, hcolor, lcolor, mdc)
	
	# top left
	mdc.SetPen(wx.Pen(hcolor, 1))
	mdc.DrawLine(0, 0, width, 0)
	mdc.DrawLine(0, 0, 0, height)
	
	# bottom right
	mdc.SetPen(wx.Pen(lcolor, 1))
	mdc.DrawLine(1, height-1, width-1, height-1)
	mdc.DrawLine(width-1, 1, width-1, height-1)
	
	# header title
	if not anode.panel.iconicMode:
		mdc.DrawText(anode.name, headerh, dh)
	else:
		tw = dc.GetFullTextExtent(str(anode.icon))[0]
		mdc.DrawText(anode.icon, (width-tw)/2, dh)
	
	ahh = headerh-dh*2
	
	maxcount = max(len(anode.in_params), len(anode.out_params))
	
	# in params
	count = 1
	for inp in anode.in_params:
		pname = str(inp["name"])
		ptype = str(inp["type"])
		mdc.DrawText(pname, headerh, dh+count*headerh)
		
		mdc.SetPen(wx.Pen(hcolor, 1))
		mdc.SetBrush(wx.Brush(TypeColors.get(ptype, wx.CYAN)))
		mdc.DrawRectangle(dh, count*headerh+dh, ahh, ahh)
		mdc.SetBrush(wx.Brush(color))
		
		if count < maxcount:
			SunkenLine(0, (count+1)*headerh, col1+headerh*2, hcolor, lcolor, mdc)
		count += 1		
	
	# out params
	count = 1
	for inp in anode.out_params:
		pname = str(inp["name"])
		ptype = str(inp["type"])
		mdc.DrawText(pname, col1+headerh*3, dh+count*headerh)
		
		ahh = headerh-dh*2
		
		mdc.SetPen(wx.Pen(hcolor, 1))
		mdc.SetBrush(wx.Brush(TypeColors.get(ptype, wx.CYAN)))
		mdc.DrawRectangle(width-dh-ahh, count*headerh+dh, ahh, ahh)
		mdc.SetBrush(wx.Brush(color))
		
		if count < maxcount:
			#SunkenLine(col1+headerh*2, (count+1)*headerh, col2+headerh*2, hcolor, lcolor, mdc)
			SunkenLine(col1+headerh*2, (count+1)*headerh, width-col1-headerh*2, hcolor, lcolor, mdc)
		count += 1		
	
	# vertical line
	mdc.SetPen(wx.Pen(lcolor, 1))
	mdc.DrawLine(col1+headerh*2, headerh+1, col1+headerh*2, height)
	mdc.SetPen(wx.Pen(hcolor, 1))
	mdc.DrawLine(col1+headerh*2+1, headerh+1, col1+headerh*2+1, height)
	
	# free resources (?)
	mdc.SetBrush(wx.NullBrush)
	
	del mdc
	if __name__ == '__main__':
		dc.DrawBitmap(bmp, top, left)
	
	return bmp

def on_paint(event):
	dc = wx.PaintDC(event.GetEventObject())
	PaintForm(node0, 50, 50, dc)

if __name__ == '__main__':

	app = wx.PySimpleApp(0)
	
	InitNodeDraw()

	frame = wx.Frame(None, -1, "Draw on Frame.")
	panel = wx.Panel(frame, -1)
	
	bgColor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
	panel.SetBackgroundColour(bgColor)
	frame.SetBackgroundColour(bgColor)
	panel.Refresh()
		
	import os
	node0 = node.Node(0, "%s/modes/Renderman SL/nodes/surface.br" % os.getcwd())
	pnl0 = NodePanel(frame, 10, 10, True, False, False)
	pnl0.assignNode(node0)
		
	wx.EVT_PAINT(panel, on_paint)
	
	frame.Show(True)
	app.MainLoop()
