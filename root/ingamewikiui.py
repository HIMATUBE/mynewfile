import app, item, player, nonplayer, ui, wndMgr, grp, math, wiki, ingamewikiconfig,\
 uiToolTip, types, constInfo, localeInfo, uiScriptLocale, dbg, sys, chat

from _weakref import proxy
from operator import truediv

"""Static pages size values!
	Please dont touch on them."""
categoryPeakWindowSize = [109, 340]
mainBoardPos = [148, 106]
mainBoardSize = [555, 361]
monsterBonusInfoPageSize = [539, 157]
itemOriginPageSize = [351, 142]

def HAS_FLAG(value, flag):
	return (value & flag) == flag

def MakeMoneyText(money):
	money = str(money)
	(original, sLen, kLen) = (money, len(money), 3)
	
	while sLen > kLen and original[sLen-kLen:] == "000":
		money = money[::-1].replace("000"[::-1], "k"[::-1], 1)[::-1]
		original = original[:sLen - kLen]
		sLen -= kLen
	
	return money

class WikiRenderTarget(ui.WikiRenderTarget):
	def __init__(self, width, height):
		self.moduleID = wiki.WIKI_RENDER_MODULE_DELETE
		
		ui.WikiRenderTarget.__init__(self)
		self.SetSize(width, height)
		
		self.ManageModelViewWindow(False)
	
	def __del__(self):
		self.ManageModelViewWindow(True)
		
		ui.WikiRenderTarget.__del__(self)
	
	def ManageModelViewWindow(self, deleteModule = False):
		self.moduleID = (wiki.GetFreeModelViewID() if deleteModule is False else wiki.WIKI_RENDER_MODULE_DELETE)
		wiki.RegisterModelViewWindow(self.moduleID, self.hWnd)
	
	def IsValidModuleID(self):
		if self.moduleID == wiki.WIKI_RENDER_MODULE_DELETE or\
			self.moduleID < wiki.WIKI_RENDER_MODULE_START:
			return False
		
		return True
	
	def SetModel(self, model_vnum):
		if self.IsValidModuleID():
			wiki.SetModelViewModel(self.moduleID, model_vnum)
	
	def SetWeaponModel(self, weapon_vnum):
		if self.IsValidModuleID():
			wiki.SetWeaponModel(self.moduleID, weapon_vnum)
	
	def SetModelForm(self, main_vnum):
		if self.IsValidModuleID():
			wiki.SetModelForm(self.moduleID, main_vnum)
	
	def SetModelHair(self, hair_vnum):
		if self.IsValidModuleID():
			wiki.SetModelHair(self.moduleID, hair_vnum)
	
	def SetModelV3Eye(self, x, y, z):
		if self.IsValidModuleID():
			wiki.SetModelV3Eye(self.moduleID, x, y, z)
	
	def SetModelV3Target(self, x, y, z):
		if self.IsValidModuleID():
			wiki.SetModelV3Target(self.moduleID, x, y, z)
	
	def Show(self):
		wndMgr.Show(self.hWnd)
		
		if self.IsValidModuleID():
			wiki.ManageModelViewVisibility(self.moduleID, True)
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)
		
		if self.IsValidModuleID():
			wiki.ManageModelViewVisibility(self.moduleID, False)

class WikiScrollBar(ui.Window):
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	CORNERS_AND_LINES_COLOR = grp.GenerateColor(0.3411, 0.3411, 0.3411, 1.0)
	
	BAR_NUMB = 9 #This is static value! Please dont touch in him.
	
	class MiddleBar(ui.DragButton):
		MIDDLE_BAR_COLOR = grp.GenerateColor(0.6470, 0.6470, 0.6470, 1.0)
		
		def __init__(self, horizontal_scroll):
			ui.DragButton.__init__(self)
			self.AddFlag("movable")
			
			self.horizontal_scroll = horizontal_scroll
			
			self.middle = ui.Bar()
			self.middle.SetParent(self)
			self.middle.AddFlag("attach")
			self.middle.AddFlag("not_pick")
			self.middle.SetColor(self.MIDDLE_BAR_COLOR)
			self.middle.SetSize(1, 1)
			self.middle.Show()
		
		def SetStaticScale(self, size):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
			
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, base_width, size)
				self.middle.SetSize(base_width, size)
			else:
				ui.DragButton.SetSize(self, size, base_height)
				self.middle.SetSize(size, base_height)
		
		def SetSize(self, selfSize, fullSize):
			(base_width, base_height) = (self.middle.GetWidth(), self.middle.GetHeight())
			
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
				self.middle.SetSize(base_width, truediv(int(selfSize), int(fullSize)) * selfSize)
			else:
				ui.DragButton.SetSize(self, truediv(int(selfSize), int(fullSize)) * selfSize, base_height)
				self.middle.SetSize(truediv(int(selfSize), int(fullSize)) * selfSize, base_height)
		
		def SetStaticSize(self, size):
			size = max(2, size)
			
			if not self.horizontal_scroll:
				ui.DragButton.SetSize(self, size, self.middle.GetHeight())
				self.middle.SetSize(size, self.middle.GetHeight())
			else:
				ui.DragButton.SetSize(self, self.middle.GetWidth(), size)
				self.middle.SetSize(self.middle.GetWidth(), size)
	
	def __init__(self, horizontal_scroll = False):
		ui.Window.__init__(self)
		
		self.horizontal_scroll = horizontal_scroll
		
		self.scrollEvent = None
		self.scrollSpeed = 1
		self.sizeScale = 1.0
		
		self.bars = []
		for i in xrange(self.BAR_NUMB):
			br = ui.Bar()
			br.SetParent(self)
			br.AddFlag("attach")
			br.AddFlag("not_pick")
			br.SetColor([self.CORNERS_AND_LINES_COLOR, self.BASE_COLOR][i == (self.BAR_NUMB-1)])
			if not (i % 2 == 0): br.SetSize(1, 1)
			br.Show()
			
			self.bars.append(br)
		
		self.middleBar = self.MiddleBar(self.horizontal_scroll)
		self.middleBar.SetParent(self)
		self.middleBar.SetMoveEvent(ui.__mem_func__(self.OnScrollMove))
		self.middleBar.Show()
	
	def OnScrollMove(self):
		if not self.scrollEvent:
			return
		
		arg = float(self.middleBar.GetLocalPosition()[1] - 1) / float(self.GetHeight() - 2 - self.middleBar.GetHeight()) if not self.horizontal_scroll else\
				float(self.middleBar.GetLocalPosition()[0] - 1) / float(self.GetWidth() - 2 - self.middleBar.GetWidth())
		
		self.scrollEvent(arg)
	
	def SetScrollEvent(self, func):
		self.scrollEvent = ui.__mem_func__(func)
	
	def SetScrollSpeed(self, speed):
		self.scrollSpeed = speed
	
	def OnMouseWheel(self, length):
		if self.IsInPosition():
			if not self.horizontal_scroll:
				val = min(max(1, self.middleBar.GetLocalPosition()[1] - (length * 0.01) * self.scrollSpeed * self.sizeScale), self.GetHeight() - self.middleBar.GetHeight() - 1)
				self.middleBar.SetPosition(1, val)
			else:
				val = min(max(1, self.middleBar.GetLocalPosition()[0] - (length * 0.01) *  self.scrollSpeed * self.sizeScale), self.GetWidth() - self.middleBar.GetWidth() - 1)
				self.middleBar.SetPosition(val, 1)
			
			self.OnScrollMove()
			return True
		
		return False
	
	def OnMouseLeftButtonDown(self):
		(xMouseLocalPosition, yMouseLocalPosition) = self.GetMouseLocalPosition()
		
		if not self.horizontal_scroll:
			if xMouseLocalPosition == 0 or xMouseLocalPosition == self.GetWidth():
				return
			
			y_pos = (yMouseLocalPosition - self.middleBar.GetHeight() / 2)
			self.middleBar.SetPosition(1, y_pos)
		else:
			if yMouseLocalPosition == 0 or yMouseLocalPosition == self.GetHeight():
				return
			
			x_pos = (xMouseLocalPosition - self.middleBar.GetWidth() / 2)
			self.middleBar.SetPosition(x_pos, 1)
		
		self.OnScrollMove()
	
	def SetSize(self, w, h):
		(width, height) = (max(3, w), max(3, h))
		
		ui.Window.SetSize(self, width, height)
		
		self.bars[0].SetSize(1, (height - 2))
		self.bars[0].SetPosition(0, 1)
		self.bars[2].SetSize((width - 2), 1)
		self.bars[2].SetPosition(1, 0)
		self.bars[4].SetSize(1, (height - 2))
		self.bars[4].SetPosition((width - 1), 1)
		self.bars[6].SetSize((width - 2), 1)
		self.bars[6].SetPosition(1, (height - 1))
		self.bars[8].SetSize((width - 2), (height - 2))
		self.bars[8].SetPosition(1, 1)
		
		self.bars[1].SetPosition(0, 0)
		self.bars[3].SetPosition((width - 1), 0)
		self.bars[5].SetPosition((width - 1), (height - 1))
		self.bars[7].SetPosition(0, (height - 1))
		
		if not self.horizontal_scroll:
			self.middleBar.SetStaticSize(width - 2)
			self.middleBar.SetSize(12, self.GetHeight())
		else:
			self.middleBar.SetStaticSize(height - 2)
			self.middleBar.SetSize(12, self.GetWidth())
		
		self.middleBar.SetRestrictMovementArea(1, 1, width - 2, height - 2)
	
	def SetScale(self, selfSize, fullSize):
		self.sizeScale = float(selfSize/fullSize)
		self.middleBar.SetSize(selfSize, fullSize)
	
	def SetStaticScale(self, r_size):
		self.middleBar.SetStaticScale(r_size)
	
	def SetPosScale(self, fScale):
		pos = (math.ceil((self.GetHeight() - 2 - self.middleBar.GetHeight()) * fScale) + 1) if not self.horizontal_scroll else\
				(math.ceil((self.GetWidth() - 2 - self.middleBar.GetWidth()) * fScale) + 1)
		
		self.SetPos(pos)
	
	def SetPos(self, pos):
		wPos = (1, pos) if not self.horizontal_scroll else (pos, 1)
		self.middleBar.SetPosition(*wPos)

class WikiBuildGrid(ui.ScriptWindow):
	"""Static values!
		Please dont touch on them."""
	GRID_WIDTH = 541
	AUTO_BUILD_GRID_COUNT = 3
	
	IMAGES_PATH = "d:/ymir work/ui/wiki/grid/"
	AUTO_BUILD_GRID_IMAGES = [IMAGES_PATH + "detail_item_3.tga", IMAGES_PATH + "detail_item.tga"]
	
	def __init__(self, parent, size, flags):
		ui.ScriptWindow.__init__(self)
		self.SetWindowName("WikiGridWindow")
		
		self.SetParent(parent)
		for flag in flags:
			self.AddFlag(flag)
		
		self.grid_elements = []
		self.LoadBackgroundParent()
		self.LoadGrid(size)
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)
	
	def LoadBackgroundParent(self):
		self.backgroundParent = ui.Window()
		self.backgroundParent.SetParent(self)
		self.backgroundParent.AddFlag("attach")
		self.backgroundParent.AddFlag("not_pick")
		self.backgroundParent.SetPosition(0, 0)
		self.backgroundParent.Show()
	
	def SetBackgroundGridSize(self, size):
		self.SetSize(*size)
		self.backgroundParent.SetSize(*size)
	
	def SetGridSize(self, new_size):
		self.LoadGrid(new_size)
	
	def CleanOldGrid(self):
		for grid in self.grid_elements:
			grid.Hide()
		
		del self.grid_elements[:]
	
	def LoadGrid(self, size):
		self.CleanOldGrid()
		
		if size <= self.AUTO_BUILD_GRID_COUNT:
			self.grid_elements.append(ui.ExpandedImageBox())
			self.grid_elements[0].SetParent(self.backgroundParent)
			self.grid_elements[0].AddFlag("attach")
			self.grid_elements[0].AddFlag("not_pick")
			self.grid_elements[0].LoadImage(self.AUTO_BUILD_GRID_IMAGES[abs(self.AUTO_BUILD_GRID_COUNT - size)])
			self.grid_elements[0].SetPosition(0,0)
			self.grid_elements[0].Show()
			
			self_size = (self.GRID_WIDTH, self.grid_elements[0].GetHeight())
			self.SetBackgroundGridSize(self_size)
		else:
			REFACT_COUNT = (size - self.AUTO_BUILD_GRID_COUNT)
			
			self.grid_elements.append(ui.ExpandedImageBox())
			self.grid_elements[0].SetParent(self.backgroundParent)
			self.grid_elements[0].AddFlag("attach")
			self.grid_elements[0].AddFlag("not_pick")
			self.grid_elements[0].LoadImage(self.IMAGES_PATH + "initial_grid.tga")
			self.grid_elements[0].SetPosition(0,0)
			self.grid_elements[0].Hide()
			
			(main_grid_pos_x, main_grid_pos_y) = self.grid_elements[0].GetLocalPosition()
			main_grid_height = self.grid_elements[0].GetHeight()
			main_grid_final_pos = main_grid_height + main_grid_pos_y
			
			for i in xrange(REFACT_COUNT):
				tmpGrid = ui.ExpandedImageBox()
				tmpGrid.SetParent(self.backgroundParent)
				tmpGrid.AddFlag("attach")
				tmpGrid.AddFlag("not_pick")
				tmpGrid.LoadImage(self.IMAGES_PATH + "grid_line.tga")
				tmpGrid.SetPosition(main_grid_pos_x, main_grid_final_pos + (tmpGrid.GetHeight() * i))
				tmpGrid.Hide()
				
				self.grid_elements.append(tmpGrid)
			
			(last_grid_pos_x, last_grid_pos_y) = self.grid_elements[-1].GetLocalPosition()
			last_grid_height = self.grid_elements[-1].GetHeight()
			
			self.grid_elements.append(ui.ExpandedImageBox())
			self.grid_elements[-1].SetParent(self.backgroundParent)
			self.grid_elements[-1].AddFlag("attach")
			self.grid_elements[-1].AddFlag("not_pick")
			self.grid_elements[-1].LoadImage(self.IMAGES_PATH + "last_grid.tga")
			self.grid_elements[-1].SetPosition(last_grid_pos_x, last_grid_pos_y + last_grid_height)
			self.grid_elements[-1].Hide()
			
			for grid in self.grid_elements:
				grid.Show()

			(last_grid_pos_x, last_grid_pos_y) = self.grid_elements[-1].GetLocalPosition()
			last_grid_height = self.grid_elements[-1].GetHeight()
			
			self_size = (self.GRID_WIDTH, last_grid_pos_y + last_grid_height)
			self.SetBackgroundGridSize(self_size)

class SubCategObject(ui.Window):
	def __init__(self, text):
		ui.Window.__init__(self)
		self.SetWindowName("SubCategObject_ListBoxEx_Item")
		
		self.mArgs = ()
		self.parent = None
		
		new_text = ""
		self.bannerFileName = None
		
		if type(text) == types.ListType:
			new_text = text[0]
			self.mArgs = text[1]
			if len(text) > 2:
				self.bannerFileName = text[2]
		
		self.textWindow = ui.Window()
		self.textWindow.SetParent(self)
		self.textWindow.AddFlag("attach")
		self.textWindow.AddFlag("not_pick")
		self.textWindow.SetPosition(2, 3)
		self.textWindow.Show()
		
		self.textLine = ui.TextLine()
		self.textLine.AddFlag("attach")
		self.textLine.AddFlag("not_pick")
		self.textLine.SetParent(self.textWindow)
		self.textLine.SetText(new_text)
		self.textLine.Show()
		
		self.cutTextLine = ui.TextLine()
		self.cutTextLine.SetParent(self.textWindow)
		self.cutTextLine.SetText(new_text)
		self.cutTextLine.Hide()
		
		self.originText = new_text
		self.cutedText = new_text
	
	def SetSize(self, w, h):
		ui.Window.SetSize(self, w, h)
		self.textWindow.SetSize(w - 2, h - 3)
		
		self.cutedText = self.GetCutText()
	
	def SetParent(self, parent):
		self.parent = proxy(parent)
		
		ui.Window.SetParent(self, parent)
	
	def OnMouseLeftButtonDown(self):
		if self.parent:
			self.parent.SelectItem(self)
	
	def GetCutText(self):
		(wL, wT, wR, wB) = self.cutTextLine.GetRenderBox()
		if wR > 0:
			i = (len(self.originText) - 1)
			
			while wR > 0:
				self.cutTextLine.SetText(self.originText[:i])
				(wL, wT, wR, wB) = self.cutTextLine.GetRenderBox()
				i -= 1
			
			self.cutTextLine.SetText(self.originText[:i].strip() + "..")
			
			(wL, wT, wR, wB) = self.cutTextLine.GetRenderBox()
			if wR > 0:
				i -= 1
			
			cut_text = (self.originText[:i] + "..")
			self.cutTextLine.SetText(self.originText)
			self.textLine.SetText(cut_text)
			
			return cut_text
		
		self.cutTextLine.SetText(self.originText)
		self.textLine.SetText(self.originText)
		
		return self.originText
	
	def OnUpdate(self):
		(wL, wT, wR, wB) = self.cutTextLine.GetRenderBox()
		currX = self.textLine.GetLocalPosition()[0]
		
		if self.IsInPosition():
			if wR > 0:
				if self.originText != self.textLine.GetText():
					self.textLine.SetText(self.originText)
				
				(wL, wT, wR, wB) = self.textLine.GetRenderBox()
				if wR > 0:
					self.textLine.SetPosition(currX - 1, 0)
		elif currX < 0:
			self.textLine.SetPosition(currX + 1, 0)
		elif self.textLine.GetText() != self.cutedText:
			self.textLine.SetText(self.cutedText)
	
	def OnRender(self):
		if self.parent.GetSelectedItem()==self:
			grp.SetColor(ui.SELECT_COLOR)
			self.OnSelectedRender()
		elif self.IsIn():
			grp.SetColor(ui.HALF_WHITE_COLOR)
			self.OnSelectedRender()
	
	def OnSelectedRender(self):
		(rLeft, rTop, rRight, rBottom) = self.GetRenderBox()
		x, y = self.GetGlobalPosition()
		
		grp.RenderBar(x + rLeft, y + rTop, self.GetWidth() - rLeft - rRight, self.GetHeight() - rBottom - rTop)

class WikiCategory(ui.Window):
	"""Static values!
		Please dont touch on them."""
	TICK_COUNT = 6
	MIN_HEIGHT = 20
	ARROW_IMG = ["d:/ymir work/ui/wiki/arrow.tga", "d:/ymir work/ui/wiki/arrow_up.tga"]
	
	LINES_COLOR = grp.GenerateColor(0.2941, 0.2941, 0.2941, 1.0)
	CORNER_COLOR = grp.GenerateColor(0.2117, 0.2117, 0.2117, 1.0)
	BASE_COLOR = grp.GenerateColor(0.0, 0.0, 0.0, 1.0)
	
	def __init__(self, owner = None):
		ui.Window.__init__(self)
		
		self.owner = (None if not owner else proxy(owner))
		
		self.expectedSize = 0
		self.currHeight = self.MIN_HEIGHT
		
		self.isAnimating = False
		self.isOpening = False
		
		self.clickEvent = None
		
		self.titleImg = ui.ExpandedImageBox()
		self.titleImg.SetParent(self)
		self.titleImg.LoadImage("d:/ymir work/ui/wiki/category.tga")
		self.titleImg.SetEventWiki(ui.__mem_func__(self.ClickExpand), "mouse_click_down")
		self.titleImg.Show()
		
		self.titleText = ui.TextLine()
		self.titleText.SetParent(self.titleImg)
		self.titleText.AddFlag("attach")
		self.titleText.AddFlag("not_pick")
		self.titleText.SetPosition(5, self.titleImg.GetHeight() / 2)
		self.titleText.Show()
		
		self.arrow = ui.ExpandedImageBox()
		self.arrow.SetParent(self.titleImg)
		self.arrow.AddFlag("attach")
		self.arrow.AddFlag("not_pick")
		self.arrow.LoadImage(self.ARROW_IMG[0])
		self.arrow.SetPosition(self.titleImg.GetWidth() - self.arrow.GetWidth() - 5, self.titleImg.GetHeight() / 2 - self.arrow.GetHeight() / 2)
		self.arrow.Show()
		
		self.expandWnd = ui.Window()
		self.expandWnd.SetParent(self)
		self.expandWnd.AddFlag("attach")
		self.expandWnd.AddFlag("not_pick")
		self.expandWnd.SetPosition(0, self.titleImg.GetHeight())
		self.expandWnd.SetSize(self.titleImg.GetWidth(), 0)
		self.expandWnd.Show()
		
		self.bars = []
		for i in xrange(self.TICK_COUNT):
			br = ui.Bar()
			br.SetParent(self.expandWnd)
			br.AddFlag("attach")
			br.AddFlag("not_pick")
			br.SetColor([self.LINES_COLOR, self.CORNER_COLOR, self.BASE_COLOR][2 if i == (self.TICK_COUNT - 1) else int(i % 2 == 0)])
			br.Show()
			
			self.bars.append(br)
		
		self.categList = ui.ListBoxEx()
		self.categList.SetParent(self.expandWnd)
		self.categList.SetItemSize(self.titleImg.GetWidth() - 6, 17)
		self.categList.SetItemStep(17)
		self.categList.SetSize(self.titleImg.GetWidth() - 6, self.MIN_HEIGHT - 1)
		self.categList.SetPosition(3, 1)
		self.categList.SetSelectEvent(ui.__mem_func__(self.OnSelectSubCategory))
		self.categList.Show()
		
		ui.Window.SetSize(self, self.titleImg.GetWidth(), self.titleImg.GetHeight())
		self.ArrangeBars(self.MIN_HEIGHT)
	
	def OnSelectSubCategory(self, elem):
		if self.owner:
			self.owner.NotifyCategorySelect(self)
		
		wikiClass = wiki.GetBaseClass()
		if wikiClass:
			if elem.bannerFileName:
				wikiClass.header.LoadImage(elem.bannerFileName)
				wikiClass.header.Show()
			else:
				wikiClass.header.Hide()
		
		if self.clickEvent:
			apply(self.clickEvent, elem.mArgs)
	
	def UnselectSubCategory(self):
		self.categList.SelectIndex(-1)
	
	def AddSubCategory(self, key, text):
		self.currHeight = (17 * (self.categList.GetItemCount() + 1) + 3)
		
		if self.expandWnd.GetHeight() > 0:
			self.ArrangeBars(self.currHeight)
			self.isAnimating = True
		
		self.categList.SetViewItemCount(self.categList.GetItemCount() + 1)
		
		item = SubCategObject(text)
		self.categList.AppendItem(item)
		
		self.categList.SetSize(self.categList.GetWidth(), self.currHeight - 1)
	
	def ClickExpand(self):
		self.arrow.LoadImage(self.ARROW_IMG[(0 if self.isOpening else 1)])
		
		self.isOpening = not self.isOpening
		self.isAnimating = True
		
		self.expandWnd.Show()
		
		self.ArrangeBars(self.currHeight if self.isOpening else 0)
	
	def OnUpdate(self):
		if not self.isAnimating:
			return
		
		h = self.expandWnd.GetHeight()
		
		if h == self.expectedSize:
			self.isAnimating = False
			
			if h == 0:
				self.expandWnd.Hide()
			
			return
		
		step = (self.currHeight / self.TICK_COUNT)
		newSize = 0
		isOpening = (False if h > self.expectedSize else True)
		
		if isOpening:
			newSize = min(self.currHeight, self.expandWnd.GetHeight() + step)
		else:
			newSize = max(0, self.expandWnd.GetHeight() - step)
		
		change = newSize - self.expandWnd.GetHeight()
		
		self.expandWnd.SetSize(self.titleImg.GetWidth(), newSize)
		ui.Window.SetSize(self, self.titleImg.GetWidth(), self.titleImg.GetHeight() + newSize)
		self.owner.NotifySizeChange(self, change, (newSize > h))
	
	def SetSize(self, width, height):
		dbg.LogBox("WikiCategory -> SetSize - unsupported function")
	
	def ArrangeBars(self, currHeight):
		self.expectedSize = currHeight
		if currHeight < self.MIN_HEIGHT:
			return
		
		currWidth = self.expandWnd.GetWidth()
		
		self.bars[0].SetSize(1, (currHeight - 1))
		self.bars[1].SetSize(1, 1)
		self.bars[1].SetPosition(0, (currHeight - 1))
		self.bars[2].SetSize((currWidth - 2), 1)
		self.bars[2].SetPosition(1, (currHeight - 1))
		self.bars[3].SetSize(1, 1)
		self.bars[3].SetPosition((currWidth - 1), (currHeight - 1))
		self.bars[4].SetSize(1, (currHeight - 1))
		self.bars[4].SetPosition((currWidth - 1), 0)
		self.bars[5].SetSize((currWidth - 2), (currHeight - 1))
		self.bars[5].SetPosition(1, 0)
	
	def SetTitleName(self, text):
		self.titleText.SetText(text)
		
		pos_y = (self.titleImg.GetHeight() / 2 - self.titleText.GetTextSize()[1] / 2 - 1)
		self.titleText.SetPosition(5, pos_y)

class WikiCategories(ui.Window):
	"""Static values!
		Please dont touch on them."""
	CATEGORY_PADDING = 5
	SCROLL_SPEED = 17
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.SetSize(*categoryPeakWindowSize)
		self.SetInsideRender(True)
		
		self.scrollBar = None
		self.hideWindowsEvent = None
		self.elements = []
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
	
	def AddCategory(self, text):
		tmp = WikiCategory(self)
		tmp.SetParent(self.scrollBoard)
		tmp.SetTitleName(text)
		tmp.Show()
		
		addPadding = 0
		if len(self.elements) > 0:
			pos_y = (self.elements[-1].GetLocalPosition()[1] + self.elements[-1].GetHeight() + self.CATEGORY_PADDING)
			tmp.SetPosition(0, pos_y)
			
			addPadding = self.CATEGORY_PADDING
		
		(width, height) = (tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.scrollBoard.SetSize(width, height)
		
		self.elements.append(tmp)
		return tmp
	
	def NotifySizeChange(self, obj, amount, expanded):
		ind = len(self.elements)
		if obj in self.elements:
			ind = (self.elements.index(obj) + 1)
		
		if ind < len(self.elements):
			for i in xrange(ind, len(self.elements)):
				pos_y = (self.elements[(i - 1)].GetLocalPosition()[1] + self.elements[(i - 1)].GetHeight() + self.CATEGORY_PADDING)
				self.elements[i].SetPosition(0, pos_y)
		
		(width, height) = (self.scrollBoard.GetWidth(), (self.scrollBoard.GetHeight() + amount))
		self.scrollBoard.SetSize(width, height)
		self.UpdateScrollbar()
	
	def NotifyCategorySelect(self, obj):
		if self.hideWindowsEvent:
			self.hideWindowsEvent()
		
		for i in self.elements:
			if obj != proxy(i) and obj != i:
				i.UnselectSubCategory()
	
	def OnMouseWheel(self, length):
		if self.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - categoryPeakWindowSize[1]) * fScale * -1.0), -self.scrollBoard.GetHeight() + categoryPeakWindowSize[1]))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		scrollBoardHeight = self.scrollBoard.GetHeight()
		selfHeight = self.GetHeight()
		
		if scrollBoardHeight <= selfHeight:
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(selfHeight, scrollBoardHeight)
			
			new_pos = self.GetNewScrollBarPosition()
			if new_pos != 0:
				self.scrollBar.SetPos(new_pos)
			else:
				pos_scale = truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (scrollBoardHeight - selfHeight))
				self.scrollBar.SetPosScale(pos_scale)
			
			self.scrollBar.Show()
	
	def GetNewScrollBarPosition(self):
		if self.scrollBoard.GetLocalPosition()[1] >= 0:
			return 0
		
		out_perc = truediv(self.scrollBoard.GetLocalPosition()[1], self.scrollBoard.GetHeight())
		scroll_max_size = abs(self.GetHeight() * out_perc)
		
		return scroll_max_size
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + categoryPeakWindowSize[1]))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self, scroll):
		self.scrollBar = proxy(scroll)
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		
		self.ChangeScrollbar()

class WikiMainWeaponWindow(ui.Window):
	class WikiItem(ui.Window):
		"""Static values!
			Please dont touch on them."""
		SCROLL_SPEED = 50
		
		TABLE_COLS = [
			[131,21,40,134],
			[172,21,40,134],
			[213,21,41,134],
			[255,21,40,134],
			[296,21,40,134],
			[337,21,41,134],
			[379,21,40,134],
			[420,21,40,134],
			[461,21,41,134],
			[503,21,36,134]
		]
		
		STARTING_MAT_COUNT = 2
		
		ROW_HEIGHTS = [21, 44, 51, 17]
		ROW_START_Y = [0, 22, 67, 119]
		
		ROW_HEIGHTS_EXPANDED = {}
		for idx in range(STARTING_MAT_COUNT + 1, wiki.REFINE_MATERIAL_MAX_NUM + 1):
			ROW_HEIGHTS_EXPANDED.update({idx : ([21, 44, 42, 22], [])})
			
			for insert_values in xrange(idx - STARTING_MAT_COUNT):
				ROW_HEIGHTS_EXPANDED[idx][0].insert((2 + insert_values), 47)
			
			for build_pos in xrange(len(ROW_HEIGHTS_EXPANDED[idx][0])):
				new_pos = 0
				for idx_pos in xrange(build_pos):
					new_pos += (ROW_HEIGHTS_EXPANDED[idx][0][idx_pos] + 1)
				
				ROW_HEIGHTS_EXPANDED[idx][1].append(new_pos)
		
		def __init__(self, vnum, parent, allow_special_page = True):
			ui.Window.__init__(self)
			
			self.parent = proxy(parent)
			
			wikiBase = wiki.GetBaseClass()
			if id(self) not in wikiBase.objList:
				wikiBase.objList[long(id(self))] = proxy(self)
			
			self.scrollBoard = None
			self.scrollBar = None
			
			self.additionalLoaded = False
			self.vnum = vnum
			self.levelLimit = 0
			
			self.base = WikiBuildGrid(self, 2, ["attach", "not_pick"])
			self.base.Show()
			
			item.SelectItem(self.vnum)
			allow_increase_vnum = wiki.CanIncrRefineLevel()
			
			self.cols = []
			for (pos_x, pos_y, width, height) in self.TABLE_COLS:
				
				tmp = ui.Window()
				tmp.SetParent(self.base)
				tmp.AddFlag("attach")
				tmp.AddFlag("not_pick")
				tmp.SetPosition(pos_x, pos_y)
				tmp.SetSize(width, height)
				tmp.Show()
				
				tmp.titleWnd = ui.Window()
				tmp.titleWnd.SetParent(tmp)
				tmp.titleWnd.SetPosition(0, self.ROW_START_Y[0])
				tmp.titleWnd.SetSize(tmp.GetWidth(), self.ROW_HEIGHTS[0])
				tmp.titleWnd.SAFE_SetOverInEvent(self.parent.OnOverIn, self.vnum + (len(self.cols) if allow_increase_vnum else 0))
				tmp.titleWnd.SAFE_SetOverOutEvent(self.parent.OnOverOut)
				if wiki.GetBaseClass() and allow_special_page:
					tmp.titleWnd.SetMouseLeftButtonDownEvent(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, self.vnum, False)
				tmp.titleWnd.Show()
				
				tmp.refineText = ui.TextLine()
				tmp.refineText.SetParent(tmp.titleWnd)
				tmp.refineText.SetText("+" + str(len(self.cols)))
				tmp.refineText.SetPosition(tmp.titleWnd.GetWidth() / 2 - tmp.refineText.GetTextSize()[0] / 2, tmp.titleWnd.GetHeight() / 2 - tmp.refineText.GetTextSize()[1] / 2 - 1)
				tmp.refineText.Show()
				
				tmp.refineMat = []
				tmp.refineMatText = []
				
				for j in xrange(self.STARTING_MAT_COUNT):
					tmp.refineMat.append(ui.ExpandedImageBox())
					tmp.refineMat[j].SetParent(tmp)
					tmp.refineMat[j].Show()
					
					tmp.refineMatText.append(ui.TextLine())
					tmp.refineMatText[j].SetParent(tmp)
					tmp.refineMatText[j].SetText("-")
					tmp.refineMatText[j].SetPosition(tmp.GetWidth() / 2 - tmp.refineMatText[j].GetTextSize()[0] / 2, self.ROW_START_Y[(1 + j)] + self.ROW_HEIGHTS[(1 + j)] / 2 - tmp.refineMatText[j].GetTextSize()[1] / 2 - 1)
					tmp.refineMatText[j].Show()
				
				tmp.moneyText = ui.TextLine()
				tmp.moneyText.SetParent(tmp)
				tmp.moneyText.SetText("-")
				tmp.moneyText.SetPosition(tmp.GetWidth() / 2 - tmp.moneyText.GetTextSize()[0] / 2, self.ROW_START_Y[(self.STARTING_MAT_COUNT+1)] + self.ROW_HEIGHTS[(self.STARTING_MAT_COUNT+1)] / 2 - tmp.moneyText.GetTextSize()[1] / 2 - 1)
				tmp.moneyText.Show()
				
				self.cols.append(tmp)
			
			self.goldText = ui.TextLine()
			self.goldText.SetParent(self.base)
			self.goldText.SetText(localeInfo.WIKI_REFINEINFO_YANG_COSTS)
			self.goldText.SetPosition(49 + 81 / 2 - self.goldText.GetTextSize()[0] / 2, 21 + self.ROW_START_Y[(self.STARTING_MAT_COUNT+1)] + self.ROW_HEIGHTS[(self.STARTING_MAT_COUNT+1)] / 2 - self.goldText.GetTextSize()[1] / 2 - 1)
			self.goldText.Show()
			
			self.upgradeText = ui.TextLine()
			self.upgradeText.SetParent(self.base)
			self.upgradeText.SetText(localeInfo.WIKI_REFINEINFO_UPGRADE_COSTS)
			self.upgradeText.SetPosition(49 + 81 / 2 - self.upgradeText.GetTextSize()[0] / 2, 21 + self.ROW_START_Y[0] + self.ROW_HEIGHTS[0] / 2 - self.upgradeText.GetTextSize()[1] / 2 - 1)
			self.upgradeText.Show()
			
			for i in xrange(item.LIMIT_MAX_NUM):
				(limitType, limitValue) = item.GetLimit(i)
				if item.LIMIT_LEVEL == limitType:
					self.levelLimit = limitValue
					break
			
			self.levelText = ui.TextLine()
			self.levelText.SetParent(self.base)
			self.levelText.SetText(localeInfo.WIKI_REFINEINFO_ITEM_LEVEL % self.levelLimit)
			self.levelText.SetPosition(self.base.GetWidth() - self.levelText.GetTextSize()[0] - 8, 1 + 19 / 2 - self.levelText.GetTextSize()[1] / 2)
			self.levelText.Show()
			
			itemName = item.GetItemName()
			fnd = itemName.find("+")
			if fnd >= 0:
				itemName = itemName[:fnd].strip()
			
			self.itemNameText = ui.TextLine()
			self.itemNameText.SetParent(self.base)
			self.itemNameText.SetText(itemName)
			self.itemNameText.SetPosition(5, 1 + 19 / 2 - self.itemNameText.GetTextSize()[1] / 2)
			self.itemNameText.Show()
			
			self.itemImage = ui.ExpandedImageBox()
			self.itemImage.SetParent(self.base)
			self.itemImage.LoadImage(item.GetIconImageFileName())
			self.itemImage.SetPosition(1 + 47 / 2 - self.itemImage.GetWidth() / 2, 21 + 134 / 2 - self.itemImage.GetHeight() / 2)
			self.itemImage.Show()
			self.itemImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverIn), "mouse_over_in", self.vnum + (9 if wiki.CanIncrRefineLevel() else 0))
			self.itemImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverOut), "mouse_over_out")
			if wiki.GetBaseClass() and allow_special_page:
				self.itemImage.SetEventWiki(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), "mouse_click_down", self.parent, self.vnum, False)
			
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
			
			self.scrollBoard = ui.Window()
			self.scrollBoard.SetParent(self)
			self.scrollBoard.AddFlag("attach")
			self.scrollBoard.AddFlag("not_pick")
			self.scrollBoard.Hide()
			
			self.RegisterHorizontalScrollBar()
		
		def __del__(self):
			if wiki.GetBaseClass():
				wiki.GetBaseClass().objList.pop(long(id(self)))
			
			ui.Window.__del__(self)
		
		def GetMaterialCount(self, refine_count, retInfo):
			maxMat = self.STARTING_MAT_COUNT
			
			for i in xrange(refine_count):
				curr = 0
				
				for j in retInfo[i][1]:
					if j[0] == 0:
						continue
					
					if curr >= wiki.REFINE_MATERIAL_MAX_NUM:
						break
					
					curr += 1
				
				maxMat = max(maxMat, curr)
			
			return maxMat
		
		def ProcessRetInfo(self, retInfo, maxMat, moneyRow, useHeight, useStart, starting_col = 0):
			for i in xrange(wiki.MAX_REFINE_COUNT):
				money = MakeMoneyText(retInfo[(i+starting_col)][0])
				
				currWindow = self.cols[i+1]
				
				if self.parent:
					item.SelectItem(self.vnum)
					
					currWindow.titleWnd.SAFE_SetOverInEvent(self.parent.OnOverIn, self.vnum + ((1+i+starting_col) if wiki.CanIncrRefineLevel() else 0))
					currWindow.titleWnd.SAFE_SetOverOutEvent(self.parent.OnOverOut)
				
				currWindow.refineText.SetText("+" + str((i+1)+starting_col))
				currWindow.refineText.SetPosition(currWindow.titleWnd.GetWidth() / 2 - currWindow.refineText.GetTextSize()[0] / 2,\
										currWindow.titleWnd.GetHeight() / 2 - currWindow.refineText.GetTextSize()[1] / 2 - 1)
				
				currWindow.moneyText.SetText(money)
				currWindow.moneyText.SetPosition(currWindow.GetWidth() / 2 - currWindow.moneyText.GetTextSize()[0] / 2,\
										useStart[moneyRow] + useHeight[moneyRow] / 2 - currWindow.moneyText.GetTextSize()[1] / 2 - 1)
				
				curr = 0
				
				for j in retInfo[(i+starting_col)][1]:
					if curr >= maxMat:
						break
					
					if j[0] != 0:
						item.SelectItem(j[0])
						
						currWindow.refineMat[curr].LoadImage(item.GetIconImageFileName())
						currWindow.refineMat[curr].SetPosition(currWindow.GetWidth() / 2 - currWindow.refineMat[curr].GetWidth() / 2, useStart[curr + 1] + useHeight[curr + 1] / 2 - currWindow.refineMat[curr].GetHeight() / 2)
						currWindow.refineMat[curr].SetEventWiki(ui.__mem_func__(self.parent.OnOverIn), "mouse_over_in", j[0])
						currWindow.refineMat[curr].SetEventWiki(ui.__mem_func__(self.parent.OnOverOut), "mouse_over_out")
						
						currWindow.refineMatText[curr].SetText(str(j[1]))
						currWindow.refineMatText[curr].SetFontColor(1.0, 1.0, 1.0)
						currWindow.refineMatText[curr].SetPosition(currWindow.refineMat[curr].GetLocalPosition()[0] + currWindow.refineMat[curr].GetWidth() - currWindow.refineMatText[curr].GetTextSize()[0],\
															currWindow.refineMat[curr].GetLocalPosition()[1] + currWindow.refineMat[curr].GetHeight() - currWindow.refineMatText[curr].GetTextSize()[1])
					
					else:
						currWindow.refineMat[curr].UnloadImage()
						
						currWindow.refineMatText[curr].SetText("-")
						currWindow.refineMatText[curr].SetFontColor(0.78, 0.78, 0.78)
						currWindow.refineMatText[curr].SetPosition(currWindow.GetWidth() / 2 - currWindow.refineMatText[curr].GetTextSize()[0] / 2,\
													useStart[curr + 1] + useHeight[curr + 1] / 2 - currWindow.refineMatText[curr].GetTextSize()[1] / 2 - 1)
					curr += 1
		
		def NoticeMe(self, noticeType = [False, 0]):
			(scrollingNoticeType, starting_col) = noticeType
			(max_refine_count, retInfo) = wiki.GetRefineInfo(self.vnum)
			if not retInfo:
				return
			
			if self.itemImage and self.parent:
				item.SelectItem(self.vnum)
				
				self.itemImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverIn), "mouse_over_in", self.vnum + (max_refine_count if wiki.CanIncrRefineLevel() else 0))
				self.itemImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverOut), "mouse_over_out")
			
			maxMat = self.GetMaterialCount(max_refine_count, retInfo)
			moneyRow = (maxMat + 1)
			
			if maxMat > self.STARTING_MAT_COUNT:
				if not scrollingNoticeType:
					self.SetExpandedRow(maxMat)
				
				useHeight = self.ROW_HEIGHTS_EXPANDED[maxMat][0]
				useStart = self.ROW_HEIGHTS_EXPANDED[maxMat][1]
			else:
				useHeight = self.ROW_HEIGHTS
				useStart = self.ROW_START_Y
			
			if not scrollingNoticeType:
				self.LoadHorizontalScrollBoard(max_refine_count)
			
			self.ProcessRetInfo(retInfo, maxMat, moneyRow, useHeight, useStart, starting_col)
		
		def SetExpandedRow(self, materialCount):
			(useHeight, useStart) = self.ROW_HEIGHTS_EXPANDED[materialCount]
			oldSize = self.base.GetHeight()
			
			self.base.SetGridSize(materialCount)
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
			
			for tmp in self.cols:
				tmp.SetSize(tmp.GetWidth(), ((useStart[-1] - 2) + useHeight[-1]))
				
				tmp.refineMat = []
				tmp.refineMatText = []
				
				for j in xrange(materialCount):
					tmp.refineMat.append(ui.ExpandedImageBox())
					tmp.refineMat[j].SetParent(tmp)
					tmp.refineMat[j].Show()
				
					tmp.refineMatText.append(ui.TextLine())
					tmp.refineMatText[j].SetParent(tmp)
					tmp.refineMatText[j].SetText("-")
					tmp.refineMatText[j].SetPosition(tmp.GetWidth() / 2 - tmp.refineMatText[j].GetTextSize()[0] / 2,\
													useStart[j + 1] + useHeight[j + 1] / 2 - tmp.refineMatText[j].GetTextSize()[1] / 2 - 1)
					tmp.refineMatText[j].Show()
				
				tmp.moneyText = ui.TextLine()
				tmp.moneyText.SetParent(tmp)
				tmp.moneyText.SetText("-")
				tmp.moneyText.SetPosition(tmp.GetWidth() / 2 - tmp.moneyText.GetTextSize()[0] / 2,\
										useStart[(materialCount + 1)] + useHeight[(materialCount + 1)] / 2 - tmp.moneyText.GetTextSize()[1] / 2 - 1)
				tmp.moneyText.Show()
			
			self.goldText.SetPosition(49 + 81 / 2 - self.goldText.GetTextSize()[0] / 2, 21 + useStart[(materialCount + 1)] + useHeight[(materialCount + 1)] / 2 - self.goldText.GetTextSize()[1] / 2 - 1)
			self.itemImage.SetPosition(1 + 47 / 2 - self.itemImage.GetWidth() / 2, 10 + (self.base.GetHeight() / 2) - (self.itemImage.GetHeight() / 2))
			
			if self.parent:
				self.parent.ChangeElementSize(self, self.base.GetHeight() - oldSize)
		
		def LoadHorizontalScrollBoard(self, max_refine_count):
			(baseWidth, baseHeight) = (self.base.GetWidth(), self.base.GetHeight())
			scrollBoardHeight = 7
			
			if max_refine_count > wiki.MAX_REFINE_COUNT and\
				self.scrollBoard and self.scrollBar:
				
				self.SetSize(baseWidth, baseHeight + (scrollBoardHeight - 1))
				
				self.scrollBoard.SetSize(baseWidth, scrollBoardHeight)
				self.scrollBoard.SetPosition(0, (baseHeight - 1))
				self.scrollBoard.Show()
				
				size_perc = truediv(wiki.MAX_REFINE_COUNT, max_refine_count)
				new_size = int(size_perc * self.scrollBoard.GetWidth())
				
				self.scrollBar.SetSize(self.scrollBoard.GetWidth(), self.scrollBoard.GetHeight())
				self.scrollBar.SetStaticScale(new_size)
				self.scrollBar.SetPosScale(0.0)
				self.scrollBar.Show()
				
				if self.parent:
					self.parent.ChangeElementSize(self, (scrollBoardHeight - 1))
			else:
				self.SetSize(baseWidth, baseHeight)
				self.scrollBoard.Hide()
				
				if self.parent:
					self.parent.ChangeElementSize(self, self.GetHeight() - baseHeight)
		
		def RegisterHorizontalScrollBar(self):
			if not self.scrollBoard:
				return
			
			self.scrollBar = WikiScrollBar(True)
			self.scrollBar.SetParent(self.scrollBoard)
			self.scrollBar.SetPosition(0, 0)
			self.scrollBar.SetScrollEvent(self.OnScrollBar)
			self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
			self.scrollBar.Show()
		
		def OnScrollBar(self, fScale):
			(max_refine_count, _) = wiki.GetRefineInfo(self.vnum)
			
			if max_refine_count <= wiki.MAX_REFINE_COUNT:
				return
			
			starting_col = int(fScale * (max_refine_count - wiki.MAX_REFINE_COUNT))
			self.NoticeMe([True, starting_col])
		
		def OnRender(self):
			if self.additionalLoaded:
				return
			
			if wiki.IsSet(self.vnum) or not hasattr(self.parent, "loadFrom") or\
				self.parent.loadFrom == self.parent.loadTo:
				self.additionalLoaded = True
				wiki.LoadInfo(long(id(self)), self.vnum)

	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 1
	
	classButtonsPath = "d:/ymir work/ui/wiki/class_buttons/"
	if app.INGAME_WIKI_WOLFMAN:
		classButtonsPath += "ingame_wiki_wolfman/"
	
	CLASS_BUTTONS = [
		[
			item.ITEM_ANTIFLAG_WARRIOR,
			classButtonsPath + "class_w_normal.tga",
			classButtonsPath + "class_w_hover.tga",
			classButtonsPath + "class_w_selected.tga"
		],
		[
			item.ITEM_ANTIFLAG_ASSASSIN,
			classButtonsPath + "class_n_normal.tga",
			classButtonsPath + "class_n_hover.tga",
			classButtonsPath + "class_n_selected.tga"
		],
		[
			item.ITEM_ANTIFLAG_SHAMAN,
			classButtonsPath + "class_s_normal.tga",
			classButtonsPath + "class_s_hover.tga",
			classButtonsPath + "class_s_selected.tga"
		],
		[
			item.ITEM_ANTIFLAG_SURA,
			classButtonsPath + "class_su_normal.tga",
			classButtonsPath + "class_su_hover.tga",
			classButtonsPath + "class_su_selected.tga"
		]
	]
	
	if app.INGAME_WIKI_WOLFMAN:
		lWolfmanClassButtons = [
			[
				item.ITEM_ANTIFLAG_WOLFMAN,
				classButtonsPath + "class_l_normal.tga",
				classButtonsPath + "class_l_hover.tga",
				classButtonsPath + "class_l_selected.tga"
			]
		]
		
		CLASS_BUTTONS.extend(lWolfmanClassButtons)
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.toolTip = uiToolTip.ItemToolTip()
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.scrollBar = None
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.currFlag = 0
		self.currCateg = 0
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 50 - 10)
		self.peekWindow.SetPosition(5, 50)
		self.peekWindow.SetInsideRender(True)
		self.peekWindow.Show()
		
		self.categWindow = ui.Window()
		self.categWindow.SetParent(self)
		self.categWindow.AddFlag("attach")
		self.categWindow.AddFlag("not_pick")
		self.categWindow.Show()
		
		self.classBtns = []
		for info in self.CLASS_BUTTONS:
			idx = len(self.classBtns)
			
			self.classBtns.append(ui.RadioButton())
			self.classBtns[idx].SetParent(self.categWindow)
			self.classBtns[idx].SetUpVisual(info[1])
			self.classBtns[idx].SetOverVisual(info[2])
			self.classBtns[idx].SetDownVisual(info[3])
			self.classBtns[idx].SetEvent(ui.__mem_func__(self.OnSelectCateg), proxy(self.classBtns[idx]), info[0])
			self.classBtns[idx].SetPosition(self.categWindow.GetWidth() + 5 * self.CLASS_BUTTONS.index(info), 0)
			self.classBtns[idx].Show()
			
			self.categWindow.SetSize(self.categWindow.GetWidth() + self.classBtns[idx].GetWidth(), self.classBtns[idx].GetHeight())
		
		self.categWindow.SetSize(self.categWindow.GetWidth() + 5 * (len(self.CLASS_BUTTONS) - 1), self.categWindow.GetHeight())
		self.categWindow.SetPosition(self.GetWidth() / 2 - self.categWindow.GetWidth() / 2, 10)
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
		
		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Show(self, categID):
		wndMgr.Show(self.hWnd)
		
		isChanged = (not categID == self.currCateg)
		self.currCateg = categID
		
		if not self.isOpened:
			self.isOpened = True
			
			if len(self.classBtns):
				self.OnSelectCateg(proxy(self.classBtns[0]), self.CLASS_BUTTONS[0][0])
		else:
			self.loadTo = wiki.LoadClassItems(self.currCateg, self.currFlag)
			
			if self.loadFrom > self.loadTo or isChanged:
				del self.elements[:]
				
				self.scrollBoard.SetSize(0, 0)
				self.UpdateScrollbar()
				self.loadFrom = 0
	
	def OnOverIn(self, vnum):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)], 0)
	
	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()
	
	def OnSelectCateg(self, btn, flag):
		self.currFlag = flag
		
		for tmpBtn in self.classBtns:
			tmpBtn.SetUp() if proxy(tmpBtn) != btn else tmpBtn.Down()
		
		del self.elements[:]
		
		self.scrollBoard.SetSize(0, 0)
		self.UpdateScrollbar()
		
		self.loadTo = wiki.LoadClassItems(self.currCateg, self.currFlag)
		self.loadFrom = 0
	
	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in wiki.ChangePage(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE)):
				self.AddItem(i)
				self.loadFrom += 1
	
	def ChangeElementSize(self, elem, sizeDiff):
		foundItem = False
		
		for i in self.elements:
			if elem != i and not foundItem:
				continue
			elif elem == i:
				foundItem = True
				continue
			
			i.SetPosition(i.GetLocalPosition()[0],\
							i.GetLocalPosition()[1] + sizeDiff)
		
		if foundItem:
			self.scrollBoard.SetSize(elem.GetWidth(), self.scrollBoard.GetHeight() + sizeDiff)
			self.UpdateScrollbar()
	
	def AddItem(self, vnum):
		startRefineVnum = wiki.GetWikiItemStartRefineVnum(vnum)
		vnum = startRefineVnum if startRefineVnum != 0 else (int(vnum / 10) * 10)
		
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		item.SelectItem(vnum)
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		
		addPadding = 0
		totalElem = len(self.elements)
		if totalElem > 0:
			lastIndex = 0
			
			for i in xrange(totalElem):
				if self.elements[i].levelLimit < tmp.levelLimit or self.elements[i].levelLimit == tmp.levelLimit and self.elements[i].vnum < tmp.vnum:
					break
				
				lastIndex += 1
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
							(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(),\
								self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			val = int((length * 0.01) * self.SCROLL_SPEED)
			self.UpdateScrollbar(val)
			
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.peekWindow.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.peekWindow.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class ChestPeekWindow(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_X_PADDING = 0
	ELEM_PADDING = 0
	SCROLL_SPEED = 25
	ELEM_PER_LINE = 11
	
	def __init__(self, parent, width, height, sendParent = True):
		ui.Window.__init__(self)
		
		self.SetSize(width, height)
		
		self.parent = proxy(parent)
		self.sendParent = sendParent
		
		self.elements = []
		self.posMap = {}
		self.scrollBar = None
		
		self.mOverInEvent = None
		self.mOverOutEvent = None
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(width-6, self.GetHeight())
		self.peekWindow.SetPosition(0, 0)
		self.peekWindow.Show()
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
	
	def AddItem(self, vnumFrom, vnumTo):
		if not self.scrollBar:
			self.RegisterScrollBar()
		
		metinSlot = [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)]
		if vnumFrom == 8:
			vnumFrom = 70104
			metinSlot[0] = vnumTo
		
		item.SelectItem(vnumFrom)
		
		tmp = ui.ExpandedImageBox()
		tmp.SetParent(self.scrollBoard)
		tmp.LoadImage(item.GetIconImageFileName())
		tmp.SetEvent(self.mOverInEvent, "mouse_over_in", vnumFrom, metinSlot)
		tmp.SetEvent(self.mOverOutEvent, "mouse_over_out")
		
		if wiki.GetBaseClass():
			vnumEvent = -1
			
			if (item.GetItemType() == item.ITEM_TYPE_WEAPON or item.GetItemType() == item.ITEM_TYPE_ARMOR):
				startRefineVnum = wiki.GetWikiItemStartRefineVnum(vnumFrom)
				vnumEvent = startRefineVnum if startRefineVnum != 0 else (int(vnumFrom / 10) * 10)
			else:
				vnumEvent = vnumFrom
			
			if vnumEvent != -1:
				if not self.sendParent:
					tmp.SetEventWiki(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), "mouse_click_down", None, vnumEvent, False)
				else:
					if hasattr(self.parent, "parent"):
						tmp.SetEventWiki(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), "mouse_click_down", self.parent.parent, vnumEvent, False)
					else:
						tmp.SetEventWiki(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), "mouse_click_down", self.parent, vnumEvent, False)
			
		tmp.itemSize = item.GetItemSize()[1]
		tmp.vnum = vnumFrom
		
		tmpDropText = ui.TextLine()
		tmpDropText.SetParent(tmp)
		tmpDropText.AddFlag("attach")
		tmpDropText.AddFlag("not_pick")
		tmpDropText.SetText((MakeMoneyText(vnumTo) if vnumFrom == 1 else (str(vnumTo) if vnumTo else "")))
		tmpDropText.SetPosition(tmp.GetWidth() - tmpDropText.GetTextSize()[0],\
									tmp.GetHeight() - tmpDropText.GetTextSize()[1])
		
		totalElem = len(self.elements)
		if totalElem > 0:
			currAdd = 0
			
			while True:
				if currAdd in self.posMap:
					currAdd += 1
					continue
				
				break
			
			totalLine = (currAdd % self.ELEM_PER_LINE)
			currH = (math.floor(currAdd / self.ELEM_PER_LINE) * (32 + self.ELEM_PADDING))
			
			for i in xrange(tmp.itemSize):
				self.posMap[currAdd + i * self.ELEM_PER_LINE] = True
			
			tmp.SetPosition(1 + totalLine * (36 + self.ELEM_X_PADDING), 0 + currH)
		else:
			for i in xrange(tmp.itemSize):
				self.posMap[i * self.ELEM_PER_LINE] = True
			
			tmp.SetPosition(1, 0)
		
		tmp.Show()
		tmpDropText.Show()
		
		self.elements.append((tmp, tmpDropText))
		
		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(self.scrollBoard.GetHeight(), tmp.GetLocalPosition()[1] + tmp.GetHeight()))
		self.UpdateScrollbar()
		
		return tmp
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			if self.scrollBar and self.scrollBar.IsShow():
				self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
				return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1,\
									self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(5, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiMainChestWindow(ui.Window):
	class WikiItem(ui.Window):
		def __init__(self, vnum, parent):
			ui.Window.__init__(self)
			
			self.parent = proxy(parent)
			self.vnum = vnum
			self.additionalLoaded = False
			
			wikiBase = wiki.GetBaseClass()
			if id(self) not in wikiBase.objList:
				wikiBase.objList[long(id(self))] = proxy(self)
			
			self.base = ui.ExpandedImageBox()
			self.base.SetParent(self)
			self.base.AddFlag("attach")
			self.base.AddFlag("not_pick")
			self.base.LoadImage("d:/ymir work/ui/wiki/detail_chest.tga")
			self.base.Show()
			
			self.chestImage = ui.ExpandedImageBox()
			self.chestImage.SetParent(self.base)
			self.chestImage.LoadImage(item.GetIconImageFileName())
			self.chestImage.SetPosition(1 + 47 / 2 - self.chestImage.GetWidth() / 2,\
									1 + 87 / 2 - self.chestImage.GetHeight() / 2)
			self.chestImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverIn), "mouse_over_in", self.vnum)
			self.chestImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverOut), "mouse_over_out")
			self.chestImage.Show()
			
			self.dropList = ChestPeekWindow(self, 401, 66)
			self.dropList.AddFlag("attach")
			self.dropList.SetParent(self.base)
			self.dropList.SetPosition(49, 22)
			self.dropList.mOverInEvent = ui.__mem_func__(self.parent.OnOverIn)
			self.dropList.mOverOutEvent = ui.__mem_func__(self.parent.OnOverOut)
			self.dropList.Show()
			
			self.originTextHead = ui.TextLine()
			self.originTextHead.SetParent(self.base)
			self.originTextHead.AddFlag("attach")
			self.originTextHead.AddFlag("not_pick")
			self.originTextHead.SetText(localeInfo.WIKI_CHESTINFO_ORIGIN)
			self.originTextHead.SetPosition(451 + 89 / 2 - self.originTextHead.GetTextSize()[0] / 2,\
									1 + 20 / 2 - self.originTextHead.GetTextSize()[1] / 2 - 1)
			self.originTextHead.Show()
			
			self.contentText = ui.TextLine()
			self.contentText.SetParent(self.base)
			self.contentText.AddFlag("attach")
			self.contentText.AddFlag("not_pick")
			self.contentText.SetText(localeInfo.WIKI_CHESTINFO_CONTENTOF % item.GetItemName())
			self.contentText.SetPosition(49 + 401 / 2 - self.contentText.GetTextSize()[0] / 2,\
									1 + 20 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)
			self.contentText.Show()
			
			self.originText = ui.TextLine()
			self.originText.SetParent(self.base)
			self.originText.AddFlag("attach")
			self.originText.AddFlag("not_pick")
			self.originText.SetText("-")
			self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2,\
									22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
			self.originText.Show()
			
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
		
		def __del__(self):
			if wiki.GetBaseClass():
				wiki.GetBaseClass().objList.pop(long(id(self)))
			
			ui.Window.__del__(self)
		
		def __GenerateMultiLine(self, text, maxWidth):
			currText = self.__GenerateSingleLine()
			textHolder = []
			
			tempText = ui.TextLine()
			tempText.Hide()
			
			splt = text.split(" ")
			currText.SetText(splt[0])
			splt = splt[1:]
			for i in splt:
				tempText.SetText(" " + i)
				if tempText.GetTextSize()[0] + currText.GetTextSize()[0] > maxWidth:
					currText.AdjustSize()
					textHolder.append(currText)
					currText = self.__GenerateSingleLine()
					currText.SetText(i)
				else:
					currText.SetText(currText.GetText() + " " + i)
			
			textHolder.append(currText)
			return textHolder
		
		def __GenerateSingleLine(self):
			text = ui.TextLine()
			text.SetParent(self.base)
			text.Show()
			return text
		
		def NoticeMe(self):
			ret = wiki.GetChestInfo(self.vnum)
			allow_lst = (len(ret) > 2)
			
			if not allow_lst:
				(dwOrigin, isCommon) = ret
			else:
				(dwOrigin, isCommon, lst) = ret
			
			self.originText.Hide()
			self.multiHolder = []
			
			if isCommon:
				self.multiHolder = self.__GenerateMultiLine(localeInfo.WIKI_CHESTINFO_COMMON_DROP, 66)
			elif dwOrigin:
				self.multiHolder = self.__GenerateMultiLine(nonplayer.GetMonsterName(dwOrigin), 66)
			else:
				self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2, 22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
				self.originText.Show()
			
			for i in self.multiHolder:
				totalH = self.multiHolder[0].GetTextSize()[1] * len(self.multiHolder) + 3 * (len(self.multiHolder) - 1)
				i.SetPosition(451 + 89 / 2 - i.GetTextSize()[0] / 2, 22 + 66 / 2 - totalH / 2 + 3 * self.multiHolder.index(i) + i.GetTextSize()[1] * self.multiHolder.index(i))
			
			if not allow_lst:
				return
			
			sizeLst = []
			orderedLst = []
			otherStuff = []
			
			for i in lst:
				if i[0] < wiki.CONTROL_ITEM_VNUM:
					otherStuff.append(i[:])
					continue
				
				item.SelectItem(i[0])
				size = item.GetItemSize()[1]
				
				lastPos = 0
				for k in xrange(len(sizeLst)):
					if sizeLst[k] < size:
						break
					
					lastPos += 1
				
				sizeLst.insert(lastPos, size)
				orderedLst.insert(lastPos, i[:])
			
			for i in orderedLst:
				count = (i[1] if i[1] > 1 else 0)
				self.dropList.AddItem(i[0], count)
			
			for i in otherStuff:
				self.dropList.AddItem(i[0], i[1])
		
		def OnRender(self):
			if self.additionalLoaded:
				return
			
			if wiki.IsSet(self.vnum) or self.parent.loadFrom == self.parent.loadTo:
				self.additionalLoaded = True
				wiki.LoadInfo(long(id(self)), self.vnum)
	
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 1
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.toolTip = uiToolTip.ItemToolTip()
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.scrollBar = None
		
		self.chestVnums = []
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 15)
		self.peekWindow.SetPosition(5, 5)
		self.peekWindow.SetInsideRender(True)
		self.peekWindow.Show()
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
		
		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Show(self, vnums):
		wndMgr.Show(self.hWnd)
		
		isChanged = (not len(vnums) == len(self.chestVnums))
		
		if not isChanged:
			for i in vnums:
				if i not in self.chestVnums:
					isChanged = True
					break
		
		if not isChanged:
			for i in self.chestVnums:
				if i not in vnums:
					isChanged = True
					break
		
		self.chestVnums = vnums[:]
		self.loadTo = len(self.chestVnums)
		
		if not self.isOpened:
			self.isOpened = True
			self.loadFrom = 0
		
		if self.loadFrom > self.loadTo or isChanged:
			del self.elements[:]
			self.loadFrom = 0
			
			self.scrollBoard.SetSize(0, 0)
			self.UpdateScrollbar()
	
	def OnOverIn(self, vnum, metinSlot = [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)]):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, metinSlot, 0)
	
	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()
	
	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in xrange(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE)):
				if type(self.chestVnums[i]) == types.ListType:
					for idx in self.chestVnums[i]:
						self.AddItem(idx)
				else:
					self.AddItem(self.chestVnums[i])
				self.loadFrom += 1
	
	def AddItem(self, vnum):
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		item.SelectItem(vnum)
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		
		addPadding = 0
		totalElem = len(self.elements)
		
		if totalElem > 0:
			lastIndex = totalElem
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
					(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiMainBossWindow(ui.Window):
	class WikiItem(ui.Window):
		def __init__(self, vnum, parent):
			ui.Window.__init__(self)
			
			self.parent = proxy(parent)
			self.vnum = vnum
			
			wikiBase = wiki.GetBaseClass()
			if id(self) not in wikiBase.objList:
				wikiBase.objList[long(id(self))] = proxy(self)
			
			self.additionalLoaded = False
			
			self.base = ui.ExpandedImageBox()
			self.base.SetParent(self)
			self.base.AddFlag("attach")
			self.base.AddFlag("not_pick")
			self.base.LoadImage("d:/ymir work/ui/wiki/detail_chest.tga")
			self.base.Show()
			
			self.modelView = WikiRenderTarget(47, 87)
			self.modelView.SetParent(self.base)
			self.modelView.SetPosition(1 + 47 / 2 - self.modelView.GetWidth() / 2,\
								1 + 87 / 2 - self.modelView.GetHeight() / 2)
			if wiki.GetBaseClass():
				self.modelView.SetMouseLeftButtonDownEvent(ui.__mem_func__(wiki.GetBaseClass().OpenSpecialPage), self.parent, self.vnum, True)
			self.modelView.Hide()
			
			self.dropList = ChestPeekWindow(self, 401, 66)
			self.dropList.AddFlag("attach")
			self.dropList.SetParent(self.base)
			self.dropList.SetPosition(49, 22)
			self.dropList.mOverInEvent = ui.__mem_func__(self.parent.OnOverIn)
			self.dropList.mOverOutEvent = ui.__mem_func__(self.parent.OnOverOut)
			self.dropList.Show()
			
			self.originTextHead = ui.TextLine()
			self.originTextHead.SetParent(self.base)
			self.originTextHead.AddFlag("attach")
			self.originTextHead.AddFlag("not_pick")
			self.originTextHead.SetText(localeInfo.WIKI_CHESTINFO_ORIGIN)
			self.originTextHead.SetPosition(451 + 89 / 2 - self.originTextHead.GetTextSize()[0] / 2,\
										1 + 20 / 2 - self.originTextHead.GetTextSize()[1] / 2 - 1)
			self.originTextHead.Show()
			
			self.contentText = ui.TextLine()
			self.contentText.SetParent(self.base)
			self.contentText.AddFlag("attach")
			self.contentText.AddFlag("not_pick")
			self.contentText.SetText(localeInfo.WIKI_MONSTERINFO_DROPLISTOF % nonplayer.GetMonsterName(self.vnum))
			self.contentText.SetPosition(49 + 401 / 2 - self.contentText.GetTextSize()[0] / 2,\
										1 + 20 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)
			self.contentText.Show()
			
			self.originText = ui.TextLine()
			self.originText.SetParent(self.base)
			self.originText.AddFlag("attach")
			self.originText.AddFlag("not_pick")
			self.originText.SetText("-")
			self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2,\
										22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
			self.originText.Show()
			
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
		
		def __del__(self):
			if wiki.GetBaseClass():
				wiki.GetBaseClass().objList.pop(long(id(self)))
			
			ui.Window.__del__(self)
		
		def __GenerateMultiLine(self, text, maxWidth):
			currText = self.__GenerateSingleLine()
			textHolder = []
			
			tempText = ui.TextLine()
			tempText.Hide()
			
			splt = text.split(" ")
			currText.SetText(splt[0])
			splt = splt[1:]
			for i in splt:
				tempText.SetText(" " + i)
				if tempText.GetTextSize()[0] + currText.GetTextSize()[0] > maxWidth:
					currText.AdjustSize()
					textHolder.append(currText)
					currText = self.__GenerateSingleLine()
					currText.SetText(i)
				else:
					currText.SetText(currText.GetText() + " " + i)
			
			textHolder.append(currText)
			return textHolder
		
		def __GenerateSingleLine(self):
			text = ui.TextLine()
			text.SetParent(self.base)
			text.Show()
			return text
		
		def NoticeMe(self):
			lst = wiki.GetMobInfo(self.vnum)
			if not lst:
				return
			
			self.originText.SetPosition(451 + 89 / 2 - self.originText.GetTextSize()[0] / 2, 22 + 66 / 2 - self.originText.GetTextSize()[1] / 2 - 1)
			self.originText.Show()
			
			sizeLst = []
			orderedLst = []
			
			for i in lst:
				if i[0] < wiki.CONTROL_ITEM_VNUM:
					continue
				
				for j in orderedLst:
					if j[0] == i[0]:
						continue
				
				item.SelectItem(i[0])
				size = item.GetItemSize()[1]
				
				lastPos = 0
				for k in xrange(len(sizeLst)):
					if sizeLst[k] < size:
						break
					
					lastPos += 1
				
				sizeLst.insert(lastPos, size)
				orderedLst.insert(lastPos, i[:])
			
			for i in orderedLst:
				count = (i[1] if i[1] > 1 else 0)
				self.dropList.AddItem(i[0], count)
		
		def OnRender(self):
			if self.additionalLoaded:
				return
			
			if wiki.IsSet(self.vnum, True) or self.parent.loadFrom == self.parent.loadTo:
				self.additionalLoaded = True
				
				self.modelView.SetModel(self.vnum)
				self.modelView.Show()
				
				wiki.LoadInfo(long(id(self)), self.vnum, True)
	
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 2
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.toolTip = uiToolTip.ItemToolTip()
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.scrollBar = None
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.mobtypes = 0
		self.fromlvl = 0
		self.tolvl = 0
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 15)
		self.peekWindow.SetPosition(5, 5)
		self.peekWindow.SetInsideRender(True)
		self.peekWindow.Show()
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
		
		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Show(self, mobtypes, fromlvl, tolvl):
		wndMgr.Show(self.hWnd)
		
		isChanged = True if not (mobtypes == self.mobtypes and\
								fromlvl == self.fromlvl and tolvl == self.tolvl) else False
		
		self.mobtypes = mobtypes
		self.fromlvl = fromlvl
		self.tolvl = tolvl
		self.loadTo = wiki.LoadClassMobs(mobtypes, fromlvl, tolvl)
		
		if not self.isOpened:
			self.isOpened = True
			self.loadFrom = 0
		
		if self.loadFrom > self.loadTo or isChanged:
			del self.elements[:]
			self.loadFrom = 0
			
			self.scrollBoard.SetSize(0, 0)
			self.UpdateScrollbar()
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)
	
	def OnOverIn(self, vnum, metinSlot = [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)]):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, metinSlot, 0)
	
	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()
	
	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in wiki.ChangePage(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE), True):
				self.AddItem(i)
				self.loadFrom += 1
	
	def AddItem(self, vnum):
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		
		addPadding = 0
		totalElem = len(self.elements)
		
		if totalElem > 0:
			lastIndex = 0
			
			for i in xrange(totalElem):
				if self.elements[i].vnum < tmp.vnum:
					break
				
				lastIndex += 1
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
						(0 if i ==0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1,\
								self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiMonsterBonusInfoWindow(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 2

	RACE_FLAG_TO_NAME = {
		nonplayer.RACE_FLAG_ANIMAL : localeInfo.WIKI_MONSTERINFO_RACE_ANIMAL,
		nonplayer.RACE_FLAG_UNDEAD : localeInfo.WIKI_MONSTERINFO_RACE_UNDEAD,
		nonplayer.RACE_FLAG_DEVIL : localeInfo.WIKI_MONSTERINFO_RACE_DEVIL,
		nonplayer.RACE_FLAG_HUMAN : localeInfo.WIKI_MONSTERINFO_RACE_HUMAN,
		nonplayer.RACE_FLAG_ORC : localeInfo.WIKI_MONSTERINFO_RACE_ORC,
		nonplayer.RACE_FLAG_MILGYO : localeInfo.WIKI_MONSTERINFO_RACE_MILGYO,
		nonplayer.RACE_FLAG_TREE : localeInfo.WIKI_MONSTERINFO_RACE_TREE,
	}
	SUB_RACE_FLAG_TO_NAME = {
		nonplayer.RACE_FLAG_ATT_ELEC : localeInfo.WIKI_MONSTERINFO_RACE_ELEC,
		nonplayer.RACE_FLAG_ATT_FIRE : localeInfo.WIKI_MONSTERINFO_RACE_FIRE,
		nonplayer.RACE_FLAG_ATT_ICE : localeInfo.WIKI_MONSTERINFO_RACE_ICE,
		nonplayer.RACE_FLAG_ATT_WIND : localeInfo.WIKI_MONSTERINFO_RACE_WIND,
		nonplayer.RACE_FLAG_ATT_EARTH : localeInfo.WIKI_MONSTERINFO_RACE_EARTH,
		nonplayer.RACE_FLAG_ATT_DARK : localeInfo.WIKI_MONSTERINFO_RACE_DARK,
	}
	IMMUNE_FLAG_TO_NAME = {
		nonplayer.IMMUNE_STUN : localeInfo.WIKI_MONSTERINFO_IMMUNE_STUN,
		nonplayer.IMMUNE_SLOW : localeInfo.WIKI_MONSTERINFO_IMMUNE_SLOW,
		nonplayer.IMMUNE_CURSE : localeInfo.WIKI_MONSTERINFO_IMMUNE_CURSE,
		nonplayer.IMMUNE_POISON : localeInfo.WIKI_MONSTERINFO_IMMUNE_POISON,
		nonplayer.IMMUNE_TERROR : localeInfo.WIKI_MONSTERINFO_IMMUNE_TERROR,
	}
	
	def __init__(self, vnum):
		ui.Window.__init__(self)
		
		self.SetSize(*monsterBonusInfoPageSize)
		
		self.vnum = vnum
		
		self.elements = []
		self.scrollBar = None
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(self.GetWidth() - 8 - 6, self.GetHeight() - 6)
		self.peekWindow.SetPosition(3, 3)
		self.peekWindow.SetInsideRender(True)
		self.peekWindow.Show()
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
		
		#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
		
		(main_race, sub_race) = self.GetRaceStrings()
		(_dmin, _dmax) = nonplayer.GetMonsterDamage(self.vnum)
		(_gMin, _gMax) = nonplayer.GetMonsterGold(self.vnum)
		
		monster_level = nonplayer.GetMonsterLevel(self.vnum)
		immune_string = self.GetImmuneString()
		damageMin = localeInfo.NumberToMoneyString(_dmin)
		damageMax = localeInfo.NumberToMoneyString(_dmax)
		goldMin = localeInfo.NumberToMoneyString(_gMin)
		goldMax = localeInfo.NumberToMoneyString(_gMax)
		
		d_page_content = [
			((localeInfo.WIKI_MONSTERINFO_LEVEL % monster_level), 0),
			((localeInfo.WIKI_MONSTERINFO_MAINRACE % main_race) + " | " + (localeInfo.WIKI_MONSTERINFO_SUBRACE % sub_race), 0),
			((localeInfo.WIKI_MONSTERINFO_IMMUNE_TO % immune_string), 0),
			((localeInfo.WIKI_MONSTERINFO_DMG_HP % (damageMin, damageMax, localeInfo.NumberToMoneyString(nonplayer.GetMonsterMaxHP(self.vnum)))), 0),
			((localeInfo.WIKI_MONSTERINFO_GOLD_EXP % (goldMin, goldMax, localeInfo.NumberToMoneyString(nonplayer.GetMonsterExp(self.vnum)))), 0),
			(localeInfo.WIKI_MONSTERINFO_RESISTANCES, 0),
			((uiToolTip.GET_AFFECT_STRING(item.APPLY_RESIST_SWORD, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_SWORD))), 10),
			((uiToolTip.GET_AFFECT_STRING(item.APPLY_RESIST_TWOHAND, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_TWOHAND))), 10),
			((uiToolTip.GET_AFFECT_STRING(item.APPLY_RESIST_DAGGER, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_DAGGER))), 10),
			((uiToolTip.GET_AFFECT_STRING(item.APPLY_RESIST_BELL, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_BELL))), 10),
			((uiToolTip.GET_AFFECT_STRING(item.APPLY_RESIST_FAN, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_FAN))), 10),
			((uiToolTip.GET_AFFECT_STRING(item.APPLY_RESIST_BOW, nonplayer.GetMonsterResistValue(self.vnum, nonplayer.MOB_RESIST_BOW))), 10),
		]
		
		for (text, padding) in d_page_content:
			self.AddItem(text, padding)
		
		#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
		
		self.RegisterScrollBar()
	
	def GetImmuneString(self):
		dwImmuneFlag = nonplayer.GetMonsterImmuneFlag(self.vnum)
		
		immuneflags = ""
		for i in xrange(nonplayer.IMMUNE_FLAG_MAX_NUM):
			curFlag = 1 << i
			
			if HAS_FLAG(dwImmuneFlag, curFlag):
				if self.IMMUNE_FLAG_TO_NAME.has_key(curFlag):
					immuneflags += self.IMMUNE_FLAG_TO_NAME[curFlag] + ", "
		
		immuneflags = (immuneflags[:-2] if len(immuneflags) else localeInfo.WIKI_MONSTERINFO_IMMUNE_NOTHING)
		return immuneflags
	
	def GetRaceStrings(self):
		dwRaceFlag = nonplayer.GetMonsterRaceFlag(self.vnum)
		(mainrace, subrace) = ("", "")
		
		for i in xrange(nonplayer.RACE_FLAG_MAX_NUM):
			curFlag = 1 << i
			
			if HAS_FLAG(dwRaceFlag, curFlag):
				if self.RACE_FLAG_TO_NAME.has_key(curFlag):
					mainrace += self.RACE_FLAG_TO_NAME[curFlag] + ", "
				elif self.SUB_RACE_FLAG_TO_NAME.has_key(curFlag):
					subrace += self.SUB_RACE_FLAG_TO_NAME[curFlag] + ", "
		
		if nonplayer.IsMonsterStone(self.vnum):
			mainrace += localeInfo.WIKI_MONSTERINFO_RACE_METIN + ", "
		
		mainrace = (mainrace[:-2] if len(mainrace) else localeInfo.WIKI_MONSTERINFO_NO_RACE)
		subrace = (subrace[:-2] if len(subrace) else localeInfo.WIKI_MONSTERINFO_NO_RACE)
		
		return (mainrace, subrace)
	
	def AddItem(self, text, padding = 0):
		tmp = ui.Window()
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		tmp.SetSize(self.GetWidth() - 8, 15)
		
		tmp.img = ui.ExpandedImageBox()
		tmp.img.SetParent(tmp)
		tmp.img.AddFlag("attach")
		tmp.img.AddFlag("not_pick")
		tmp.img.LoadImage("d:/ymir work/ui/wiki/arrow_2.tga")
		tmp.img.SetPosition(padding, tmp.GetHeight() / 2 - tmp.img.GetHeight() / 2)
		tmp.img.Show()
		
		tmp.txt = ui.TextLine()
		tmp.txt.SetParent(tmp)
		tmp.txt.AddFlag("attach")
		tmp.txt.AddFlag("not_pick")
		tmp.txt.SetText(text)
		tmp.txt.SetPosition(tmp.img.GetLocalPosition()[0] + tmp.img.GetWidth() + 5,\
							tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2 - 1)
		tmp.txt.Show()
		
		addPadding = 0
		totalElem = len(self.elements)
		
		if totalElem > 0:
			lastIndex = totalElem
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,\
					(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiItemOriginInfo(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 5
	SCROLL_SPEED = 50
	ITEM_LOAD_PER_UPDATE = 2
	
	def __init__(self, vnum):
		ui.Window.__init__(self)
		
		self.SetSize(*itemOriginPageSize)
		
		self.vnum = vnum
		
		self.elements = []
		self.mainDataImage = None
		self.scrollBar = None
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(self.GetWidth() - 8 - 6, self.GetHeight() - 6)
		self.peekWindow.SetPosition(3, 3)
		self.peekWindow.SetInsideRender(True)
		self.peekWindow.Show()
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
		
		self.RegisterScrollBar()
	
	def ParseTextlines(self):
		lst = wiki.GetOriginInfo(self.vnum)
		if not lst:
			return
		
		alreadyParsed = []
		
		for (vnum, isMonster) in lst:
			bAlready = False
			
			for i in alreadyParsed:
				if i[0] == vnum and i[1] == isMonster:
					bAlready = True
					break
			
			if bAlready or not vnum:
				continue
			
			if isMonster:
				currName = nonplayer.GetMonsterName(vnum)
			else:
				item.SelectItem(vnum)
				currName = item.GetItemName()
			
			alreadyParsed.append([vnum, isMonster])
			self.AddItem(currName)
	
	def AddItem(self, text, padding = 0):
		tmp = ui.Window()
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		tmp.SetSize(self.GetWidth() - 8, 15)
		
		tmp.img = ui.ExpandedImageBox()
		tmp.img.SetParent(tmp)
		tmp.img.AddFlag("attach")
		tmp.img.AddFlag("not_pick")
		tmp.img.LoadImage("d:/ymir work/ui/wiki/arrow_2.tga")
		tmp.img.SetPosition(padding, tmp.GetHeight() / 2 - tmp.img.GetHeight() / 2)
		tmp.img.Show()
		
		tmp.txt = ui.TextLine()
		tmp.txt.SetParent(tmp)
		tmp.txt.AddFlag("attach")
		tmp.txt.AddFlag("not_pick")
		tmp.txt.SetText(text)
		tmp.txt.SetPosition(tmp.img.GetLocalPosition()[0] + tmp.img.GetWidth() + 5,
								tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2 - 1)
		tmp.txt.Show()
		
		addPadding = 0
		totalElem = len(self.elements)
		
		if totalElem > 0:
			lastIndex = totalElem
			
			self.elements.insert(lastIndex, tmp)
			totalElem += 1
			
			for i in xrange(lastIndex, totalElem):
				self.elements[i].SetPosition(0,
						(0 if i == 0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + self.ELEM_PADDING))
			
			addPadding = self.ELEM_PADDING
		else:
			self.elements.append(tmp)
		
		tmp.Show()
		
		self.scrollBoard.SetSize(tmp.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		self.UpdateScrollbar()
		
		return tmp
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class SpecialPageWindow(ui.Window):
	"""Static values!
		Please dont touch on them."""
	SCROLL_SPEED = 50
	
	def __init__(self, vnum, isMonster):
		ui.Window.__init__(self)
		
		self.toolTip = uiToolTip.ItemToolTip()
		
		wikiBase = wiki.GetBaseClass()
		if id(self) not in wikiBase.objList:
			wikiBase.objList[long(id(self))] = proxy(self)
		
		self.vnum = vnum
		self.isMonster = isMonster
		self.bonusScrollBoard = None
		
		self.bg = ui.ExpandedImageBox()
		self.bg.SetParent(self)
		self.bg.AddFlag("attach")
		self.bg.AddFlag("not_pick")
		self.bg.LoadImage("d:/ymir work/ui/wiki/detail_monster.tga")
		self.bg.Show()
		
		self.SetSize(self.bg.GetWidth(), self.bg.GetHeight())
		self.SetInsideRender(True)
		
		self.subTitleText1 = ui.TextLine()
		self.subTitleText1.SetParent(self.bg)
		self.subTitleText1.AddFlag("attach")
		self.subTitleText1.AddFlag("not_pick")
		self.subTitleText1.Show()
		
		self.subTitleText2 = ui.TextLine()
		self.subTitleText2.SetParent(self.bg)
		self.subTitleText2.AddFlag("attach")
		self.subTitleText2.AddFlag("not_pick")
		self.subTitleText2.Show()
		
		if isMonster:
			self.subTitleText1.SetText(localeInfo.WIKI_MONSTERINFO_DROPLISTOF % nonplayer.GetMonsterName(self.vnum))
			self.subTitleText2.SetText(localeInfo.WIKI_MONSTERINFO_STATISTICSOF % nonplayer.GetMonsterName(self.vnum))
			
			self.modelView = WikiRenderTarget(163, 163)
			self.modelView.SetParent(self.bg)
			self.modelView.AddFlag("attach")
			self.modelView.SetPosition(1 + 187 / 2 - 163 / 2, 1)
			self.modelView.SetModel(vnum)
			self.modelView.Show()
			
			self.itemContainer = ChestPeekWindow(self, itemOriginPageSize[0], itemOriginPageSize[1], False)
			self.itemContainer.ELEM_PER_LINE = 10
			self.itemContainer.ELEM_X_PADDING = -2
			self.itemContainer.AddFlag("attach")
			self.itemContainer.SetParent(self.bg)
			self.itemContainer.SetPosition(189, 22)
			self.itemContainer.mOverInEvent = ui.__mem_func__(self.OnOverIn)
			self.itemContainer.mOverOutEvent = ui.__mem_func__(self.OnOverOut)
			self.itemContainer.Show()
			
			self.LoadDropData()
			
			self.bonusInfo = WikiMonsterBonusInfoWindow(self.vnum)
			self.bonusInfo.SetParent(self.bg)
			self.bonusInfo.AddFlag("attach")
			self.bonusInfo.SetPosition(1, 188)
			self.bonusInfo.Show()
		else:
			item.SelectItem(self.vnum)
			
			if wiki.CanIncrRefineLevel():
				startRefineVnum = wiki.GetWikiItemStartRefineVnum(self.vnum)
				self.vnum = startRefineVnum if startRefineVnum != 0 else (int(self.vnum / 10) * 10)
			
			self.subTitleText1.SetText(localeInfo.WIKI_ITEMINFO_OPTAINEDFROM)
			self.subTitleText2.SetText(localeInfo.WIKI_ITEMINFO_REFINEINFO % item.GetItemName()[:-2])
			
			self.modelView = ui.ExpandedImageBox()
			self.modelView.SetParent(self.bg)
			self.modelView.AddFlag("attach")
			self.modelView.LoadImage(item.GetIconImageFileName())
			self.modelView.SetPosition(1 + 187 / 2 - self.modelView.GetWidth() / 2, 1 + 163 / 2 - self.modelView.GetHeight() / 2)
			self.modelView.SetEventWiki(ui.__mem_func__(self.OnOverIn), "mouse_over_in", self.vnum + (wiki.MAX_REFINE_COUNT if wiki.CanIncrRefineLevel() else 0))
			self.modelView.SetEventWiki(ui.__mem_func__(self.OnOverOut), "mouse_over_out")
			self.modelView.Show()
			
			self.bonusPeekWindow = ui.Window()
			self.bonusPeekWindow.SetParent(self.bg)
			self.bonusPeekWindow.AddFlag("attach")
			self.bonusPeekWindow.AddFlag("not_pick")
			self.bonusPeekWindow.SetPosition(0, 187)
			self.bonusPeekWindow.SetInsideRender(True)
			self.bonusPeekWindow.Show()
			
			self.bonusScrollBoard = ui.Window()
			self.bonusScrollBoard.SetParent(self.bonusPeekWindow)
			self.bonusScrollBoard.AddFlag("attach")
			self.bonusScrollBoard.AddFlag("not_pick")
			self.bonusScrollBoard.Show()
			
			self.bonusInfo = WikiMainWeaponWindow.WikiItem(self.vnum, self, False)
			self.bonusInfo.SetParent(self.bonusScrollBoard)
			self.bonusInfo.Show()
			
			self.additionalLoaded = False
			
			self.bonusPeekWindow.SetSize(self.bonusInfo.GetWidth(), self.bonusInfo.GetHeight())
			self.bonusScrollBoard.SetSize(self.bonusInfo.GetWidth(), self.bonusInfo.GetHeight())
			
			self.originInfo = WikiItemOriginInfo(self.vnum)
			self.originInfo.SetParent(self.bg)
			self.originInfo.AddFlag("attach")
			self.originInfo.SetPosition(189, 22)
			self.originInfo.Show()
		
		self.subTitleText1.SetPosition(189 + 351 / 2 - self.subTitleText1.GetTextSize()[0] / 2, 1 + 10 - self.subTitleText1.GetTextSize()[1] / 2)
		self.subTitleText2.SetPosition(1 + 539 / 2 - self.subTitleText2.GetTextSize()[0] / 2, 165 + 11 - self.subTitleText2.GetTextSize()[1] / 2)
	
	def __del__(self):
		if wiki.GetBaseClass():
			wiki.GetBaseClass().objList.pop(long(id(self)))
		
		ui.Window.__del__(self)
	
	def OnMouseWheel(self, length):
		if not self.bonusScrollBoard:
			return
		
		if self.bonusScrollBoard.GetHeight() == self.bonusPeekWindow.GetHeight():
			return
		
		if self.bonusPeekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def ChangeElementSize(self, elem, sizeDiff):
		if self.bonusScrollBoard:
			self.bonusScrollBoard.SetSize(self.bonusScrollBoard.GetWidth(), self.bonusScrollBoard.GetHeight() + sizeDiff)
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.bonusScrollBoard.GetLocalPosition()[1] + val, -self.bonusScrollBoard.GetHeight() + self.bonusPeekWindow.GetHeight()))
		if self.bonusScrollBoard:
			self.bonusScrollBoard.SetPosition(0, curr)
	
	def OnOverIn(self, vnum, metinSlot = [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)]):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.AddItemData(vnum, metinSlot, 0)
	
	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()
	
	def OnRender(self):
		if not self.isMonster and not self.additionalLoaded and wiki.IsSet(self.vnum):
			self.additionalLoaded = True
			self.originInfo.ParseTextlines()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def NoticeMe(self):
		self.LoadDropData()
	
	def LoadDropData(self):
		if not self.isMonster:
			return
		
		if not wiki.IsSet(self.vnum, True):
			wiki.LoadInfo(long(id(self)), self.vnum, True)
			return
		
		lst = wiki.GetMobInfo(self.vnum)
		if not lst:
			return
		
		sizeLst = []
		orderedLst = []
		
		for i in lst:
			if i[0] < wiki.CONTROL_ITEM_VNUM:
				continue
			
			item.SelectItem(i[0])
			size = item.GetItemSize()[1]
			
			lastPos = 0
			for k in xrange(len(sizeLst)):
				if sizeLst[k] < size:
					break
				
				lastPos += 1
			
			sizeLst.insert(lastPos, size)
			orderedLst.insert(lastPos, i[:])
		
		for i in orderedLst:
			count = (i[1] if i[1] > 1 else 0)
			self.itemContainer.AddItem(i[0], count)
	
	def Show(self):
		wndMgr.Show(self.hWnd)
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)

class SimpleTextLoader(ui.Window):
	"""Static values!
		Please dont touch on them."""
	ELEM_PADDING = 0
	SCROLL_SPEED = 50
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.images = []
		self.scrollBar = None
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(self.GetWidth() - 8 - 5, self.GetHeight() - 5)
		self.peekWindow.SetPosition(5, 5)
		self.peekWindow.SetInsideRender(True)
		self.peekWindow.Show()
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
		
		self.RegisterScrollBar()
	
	def ParseToken(self, data):
		data = data.replace(chr(10), "").replace(chr(13), "")
		if not (len(data) and data[0] == "["):
			return (False, {}, data)
		
		fnd = data.find("]")
		if fnd <= 0:
			return (False, {}, data)
		
		content = data[1:fnd]
		data = data[fnd+1:]
		
		content = content.split(";")
		container = {}
		
		for i in content:
			i = i.strip()
			splt = i.split("=")
			
			if len(splt) == 1:
				container[splt[0].lower().strip()] = True
			else:
				container[splt[0].lower().strip()] = splt[1].lower().strip()
		
		return (True, container, data)
	
	def GetColorFromString(self, strCol):
		retData = []
		dNum = 4
		hCol = long(strCol, 16)
		
		if hCol <= 0xFFFFFF:
			retData.append(1.0)
			dNum = 3
		
		for i in xrange(dNum):
			retData.append(float((hCol >> (8 * i)) & 0xFF) / 255.0)
		
		retData.reverse()
		return retData
	
	def LoadFile(self, filename):
		del self.elements[:]
		del self.images[:]
		
		self.scrollBoard.SetSize(0, 0)
		self.UpdateScrollbar()
		
		open_filename = "{}/wiki/{}".format(app.GetLocalePath(), filename)
		loadF = new_open(open_filename, 'r')
		
		for i in loadF.readlines()[1:]:
			(ret, tokenMap, i) = self.ParseToken(i)
			
			if ret:
				if tokenMap.has_key("banner_img"):
					if wiki.GetBaseClass():
						wiki.GetBaseClass().header.LoadImage(tokenMap["banner_img"])
						wiki.GetBaseClass().header.Show()
					
					tokenMap.pop("banner_img")
				
				if tokenMap.has_key("img"):
					cimg = ui.ExpandedImageBox()
					cimg.SetParent(self.scrollBoard)
					cimg.AddFlag("attach")
					cimg.AddFlag("not_pick")
					cimg.LoadImage(tokenMap["img"])
					cimg.Show()
					
					tokenMap.pop("img")
					
					x = 0
					if tokenMap.has_key("x"):
						x = int(tokenMap["x"])
						tokenMap.pop("x")
					
					y = 0
					if tokenMap.has_key("y"):
						y = int(tokenMap["y"])
						tokenMap.pop("y")
					
					if tokenMap.has_key("center_align"):
						cimg.SetPosition(self.peekWindow.GetWidth() / 2 - cimg.GetWidth() / 2, y)
						tokenMap.pop("center_align")
					elif tokenMap.has_key("right_align"):
						cimg.SetPosition(self.peekWindow.GetWidth() - cimg.GetWidth(), y)
						tokenMap.pop("right_align")
					else:
						cimg.SetPosition(x, y)
					
					self.images.append(cimg)
			
			if ret and not len(i):
				continue
			
			tmp = ui.Window()
			tmp.SetParent(self.scrollBoard)
			tmp.AddFlag("attach")
			tmp.AddFlag("not_pick")
			
			tmp.txt = ui.TextLine()
			tmp.txt.SetParent(tmp)
			if tokenMap.has_key("font_size"):
				splt = localeInfo.UI_DEF_FONT.split(":")
				tmp.txt.SetFontName(splt[0]+":"+tokenMap["font_size"])
				tokenMap.pop("font_size")
			else:
				tmp.txt.SetFontName(localeInfo.UI_DEF_FONT)
			tmp.txt.SetText(i)
			tmp.txt.Show()
			tmp.SetSize(*tmp.txt.GetTextSize())
			
			if len(i) > 0 and i[0] == "*":
				tmp.txt.SetText(i[1:])
				
				tmp.img = ui.ExpandedImageBox()
				tmp.img.SetParent(tmp)
				tmp.img.AddFlag("attach")
				tmp.img.AddFlag("not_pick")
				tmp.img.LoadImage("d:/ymir work/ui/wiki/arrow_2.tga")
				tmp.img.Show()
				
				tmp.SetSize(tmp.img.GetWidth() + 5 + tmp.txt.GetTextSize()[0], max(tmp.img.GetHeight(), tmp.txt.GetTextSize()[1]))
				tmp.img.SetPosition(0, abs(tmp.GetHeight() / 2 - tmp.img.GetHeight() / 2))
				
				tmp.txt.SetPosition(tmp.img.GetWidth() + 5, abs(tmp.GetHeight() / 2 - tmp.txt.GetTextSize()[1] / 2) - 1)
			
			if tokenMap.has_key("color"):
				fontColor = self.GetColorFromString(tokenMap["color"])
				tmp.txt.SetPackedFontColor(grp.GenerateColor(fontColor[0], fontColor[1], fontColor[2], fontColor[3]))
				
				tokenMap.pop("color")
			
			addPadding = 0
			totalElem = len(self.elements)
			
			if tokenMap.has_key("y_padding"):
				addPadding = int(tokenMap["y_padding"])
				tokenMap.pop("y_padding")
			
			if totalElem > 0:
				lastIndex = totalElem
				
				self.elements.insert(lastIndex, tmp)
				totalElem += 1
				
				for i in xrange(lastIndex, totalElem):
					self.elements[i].SetPosition(0,\
						(0 if i ==0 else self.elements[i - 1].GetLocalPosition()[1] + self.elements[i - 1].GetHeight() + addPadding))
			else:
				self.elements.append(tmp)
				tmp.SetPosition(0, addPadding)
			
			if tokenMap.has_key("center_align"):
				tmp.SetPosition(self.peekWindow.GetWidth() / 2 - tmp.GetWidth() / 2, tmp.GetLocalPosition()[1])
				tokenMap.pop("center_align")
			elif tokenMap.has_key("right_align"):
				tmp.SetPosition(self.peekWindow.GetWidth() - tmp.GetWidth(), tmp.GetLocalPosition()[1])
				tokenMap.pop("right_align")
			elif tokenMap.has_key("x_padding"):
				tmp.SetPosition(int(tokenMap["x_padding"]), tmp.GetLocalPosition()[1])
				tokenMap.pop("x_padding")
			
			tmp.Show()
			
			self.scrollBoard.SetSize(self.peekWindow.GetWidth(), self.scrollBoard.GetHeight() + addPadding + tmp.GetHeight())
		
		for i in self.images:
			mxSize = i.GetLocalPosition()[1] + i.GetHeight()
			if mxSize > self.scrollBoard.GetHeight():
				self.scrollBoard.SetSize(self.peekWindow.GetWidth(), mxSize)
		
		self.UpdateScrollbar()
		wndMgr.Show(self.hWnd)
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

class WikiMainCostumeWindow(ui.Window):
	class WikiItem(ui.Window):
		def __init__(self, vnum, parent):
			ui.Window.__init__(self)
			
			self.vnum = vnum
			self.parent = proxy(parent)
			
			self.base = ui.ExpandedImageBox()
			self.base.SetParent(self)
			self.base.AddFlag("attach")
			self.base.AddFlag("not_pick")
			self.base.LoadImage("d:/ymir work/ui/wiki/detail_item_small.tga")
			self.base.Show()
			
			self.costumeImage = ui.ExpandedImageBox()
			self.costumeImage.SetParent(self.base)
			self.costumeImage.LoadImage(item.GetIconImageFileName())
			self.costumeImage.SetPosition(1 + 125 / 2 - self.costumeImage.GetWidth() / 2,\
										1 + 120 / 2 - self.costumeImage.GetHeight() / 2)
			self.costumeImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverIn), "mouse_over_in", self.vnum)
			self.costumeImage.SetEventWiki(ui.__mem_func__(self.parent.OnOverOut), "mouse_over_out")
			self.costumeImage.Show()
			
			self.contentText = ui.TextLine()
			self.contentText.SetParent(self.base)
			self.contentText.AddFlag("attach")
			self.contentText.AddFlag("not_pick")
			self.contentText.SetText(item.GetItemName())
			self.contentText.SetPosition(1 + 125 / 2 - self.contentText.GetTextSize()[0] / 2, 122 + 18 / 2 - self.contentText.GetTextSize()[1] / 2 - 1)
			self.contentText.Show()
			
			self.SetSize(self.base.GetWidth(), self.base.GetHeight())
	
	"""Static values!
		Please dont touch on them."""
	ELEM_X_PADDING = 10
	ELEM_PADDING = 10
	SCROLL_SPEED = 25
	ELEM_PER_LINE = 4
	ITEM_LOAD_PER_UPDATE = 1
	
	def __init__(self):
		ui.Window.__init__(self)
		
		self.toolTip = uiToolTip.ItemToolTip()
		self.toolTip.AddFlag("not_pick")
		
		self.SetSize(*mainBoardSize)
		
		self.elements = []
		self.costumeVnums = []
		self.posMap = {}
		self.scrollBar = None
		
		self.isOpened = False
		self.loadFrom = 0
		self.loadTo = 0
		
		self.wikiRenderTarget = WikiRenderTarget(150, 200)
		self.wikiRenderTarget.SetParent(self.toolTip)
		self.wikiRenderTarget.AddFlag("not_pick")
		self.wikiRenderTarget.SetPosition(5, self.toolTip.toolTipHeight)
		self.wikiRenderTarget.Hide()
		
		self.peekWindow = ui.Window()
		self.peekWindow.SetParent(self)
		self.peekWindow.AddFlag("attach")
		self.peekWindow.AddFlag("not_pick")
		self.peekWindow.SetSize(541, self.GetHeight() - 15)
		self.peekWindow.SetPosition(5, 5)
		self.peekWindow.SetInsideRender(True)
		self.peekWindow.Show()
		
		self.scrollBoard = ui.Window()
		self.scrollBoard.SetParent(self.peekWindow)
		self.scrollBoard.AddFlag("attach")
		self.scrollBoard.AddFlag("not_pick")
		self.scrollBoard.Show()
		
		self.RegisterScrollBar()
	
	def OpenWindow(self):
		wndMgr.Show(self.hWnd)
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)
	
	def Show(self, vnums):
		wndMgr.Show(self.hWnd)
		
		extractedLists = []
		for i in vnums:
			if type(i) == types.ListType:
				extractedLists.append(i)
		
		for i in extractedLists:
			pos = vnums.index(i)
			
			vnums.remove(i)
			for j in xrange(len(i)):
				vnums.insert(pos + j, i[j])
		
		isChanged = (not len(vnums) == len(self.costumeVnums))
		
		if not isChanged:
			for i in vnums:
				if i not in self.costumeVnums:
					isChanged = True
					break
		
		if not isChanged:
			for i in self.costumeVnums:
				if i not in vnums:
					isChanged = True
					break
		
		self.costumeVnums = vnums[:]
		self.loadTo = len(self.costumeVnums)
		
		if not self.isOpened:
			self.isOpened = True
			self.loadFrom = 0
		
		if self.loadFrom > self.loadTo or isChanged:
			del self.elements[:]
			self.posMap = {}
			
			self.loadFrom = 0
			
			self.scrollBoard.SetSize(0, 0)
			self.UpdateScrollbar()
	
	def GetRandomChar(self):
		ASSASSINS 		= [ player.MAIN_RACE_ASSASSIN_W, player.MAIN_RACE_ASSASSIN_M ]
		WARRIORS 		= [ player.MAIN_RACE_WARRIOR_W, player.MAIN_RACE_WARRIOR_M ]
		SURAS 			= [ player.MAIN_RACE_SURA_W, player.MAIN_RACE_SURA_M ]
		SHAMANS 		= [ player.MAIN_RACE_SHAMAN_W, player.MAIN_RACE_SHAMAN_M ]
		ITEM_CHARACTERS = [ ASSASSINS, WARRIORS, SURAS, SHAMANS ]
		
		if app.INGAME_WIKI_WOLFMAN:
			WOLFMANS		= [player.MAIN_RACE_WOLFMAN_M]
			ITEM_CHARACTERS.extend([WOLFMANS])
		
		SEX_FEMALE		= 0
		SEX_MALE		= 1
		ITEM_SEX		= [ SEX_FEMALE, SEX_MALE ]
		
		#-#
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_MALE ):
			ITEM_SEX.remove( SEX_MALE )
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_FEMALE ):
			ITEM_SEX.remove( SEX_FEMALE )
		
		#-#
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_WARRIOR ):
			ITEM_CHARACTERS.remove( WARRIORS )
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_SURA ):
			ITEM_CHARACTERS.remove( SURAS )
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_ASSASSIN ):
			ITEM_CHARACTERS.remove( ASSASSINS )
		
		if item.IsAntiFlag( item.ITEM_ANTIFLAG_SHAMAN ):
			ITEM_CHARACTERS.remove( SHAMANS )
		
		if app.INGAME_WIKI_WOLFMAN:
			if item.IsAntiFlag( item.ITEM_ANTIFLAG_WOLFMAN ):
				ITEM_CHARACTERS.remove( WOLFMANS )
			
			CHAR_TYPE = ITEM_CHARACTERS[app.GetRandom(0, len(ITEM_CHARACTERS) - 1)]
			if len(CHAR_TYPE) == 1 and CHAR_TYPE[0] == player.MAIN_RACE_WOLFMAN_M:
				return player.MAIN_RACE_WOLFMAN_M
			else:
				CHAR_SEX = ITEM_SEX[app.GetRandom(0, len(ITEM_SEX) - 1)]
				if (CHAR_SEX > (len(CHAR_TYPE) - 1)):
					return CHAR_TYPE[0]
				else:
					return CHAR_TYPE[CHAR_SEX]
		else:
			return ITEM_CHARACTERS[app.GetRandom(0, len(ITEM_CHARACTERS) - 1)][ITEM_SEX[app.GetRandom(0, len(ITEM_SEX) - 1)]]

	def GetCharTypeHairCamera(self, char_type):
		if not ingamewikiconfig.HAIRSTYLE_CAMERA_CFG.has_key(char_type):
			return tuple([], [])
		
		return ingamewikiconfig.HAIRSTYLE_CAMERA_CFG[char_type]
	
	def OnOverIn(self, vnum, metinSlot = [0 for i in xrange(player.METIN_SOCKET_MAX_NUM)]):
		if not self.toolTip:
			return
		
		self.toolTip.ClearToolTip()
		self.toolTip.SetThinBoardSize(self.wikiRenderTarget.GetWidth() + 10, self.wikiRenderTarget.GetHeight() + self.toolTip.toolTipHeight)
		self.toolTip.childrenList.append(self.wikiRenderTarget)
		self.toolTip.ResizeToolTip()
		
		item.SelectItem(vnum)
		
		itemType = item.GetItemType()
		subType = item.GetItemSubType()
		char_type = self.GetRandomChar()
		
		self.wikiRenderTarget.SetModel(char_type)
		if itemType == item.ITEM_TYPE_WEAPON or itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_WEAPON:
			self.wikiRenderTarget.SetWeaponModel(vnum)
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_BODY:
			self.wikiRenderTarget.SetModelForm(vnum)
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_HAIR:
			self.wikiRenderTarget.SetModelHair(item.GetValue(3))
			(V3Eye, V3Target) = self.GetCharTypeHairCamera(char_type)
			if len(V3Eye) and len(V3Target):
				self.wikiRenderTarget.SetModelV3Eye(*V3Eye)
				self.wikiRenderTarget.SetModelV3Target(*V3Target)
		"""
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_PET:
			self.wikiRenderTarget.SetModel(item.GetValue(0))
		elif itemType == item.ITEM_TYPE_COSTUME and subType == item.COSTUME_TYPE_MOUNT:
			self.wikiRenderTarget.SetModel(item.GetValue(0))
		"""
		
		self.toolTip.AddItemData(vnum, metinSlot, 0)
		self.wikiRenderTarget.SetPosition(self.toolTip.GetWidth() / 2 - self.wikiRenderTarget.GetWidth() / 2, self.wikiRenderTarget.GetLocalPosition()[1])
		self.wikiRenderTarget.Show()
	
	def OnOverOut(self):
		if not self.toolTip:
			return
		
		self.toolTip.Hide()
	
	def OnUpdate(self):
		if self.loadFrom < self.loadTo:
			for i in xrange(self.loadFrom, min(self.loadTo, self.loadFrom + self.ITEM_LOAD_PER_UPDATE)):
				self.AddItem(self.costumeVnums[i])
				self.loadFrom += 1
	
	def AddItem(self, vnum):
		for i in self.elements:
			if vnum == i.vnum:
				return None
		
		item.SelectItem(vnum)
		
		tmp = self.WikiItem(vnum, self)
		tmp.SetParent(self.scrollBoard)
		tmp.AddFlag("attach")
		
		totalElem = len(self.elements)
		if totalElem > 0:
			currAdd = 0
			while currAdd in self.posMap:
				currAdd += 1
			
			totalLine = currAdd % self.ELEM_PER_LINE
			currH = math.floor(currAdd / self.ELEM_PER_LINE) * (tmp.GetHeight() + self.ELEM_PADDING)
			
			self.posMap[currAdd] = True
			tmp.SetPosition(1 + totalLine * (tmp.GetWidth() + self.ELEM_X_PADDING), 0 + currH)
		else:
			self.posMap[0] = True
			tmp.SetPosition(1, 0)
		
		tmp.Show()
		self.elements.append(tmp)
		
		self.scrollBoard.SetSize(self.peekWindow.GetWidth(), max(self.scrollBoard.GetHeight(), tmp.GetLocalPosition()[1] + tmp.GetHeight()))
		self.UpdateScrollbar()
	
	def OnMouseWheel(self, length):
		if self.peekWindow.IsInPosition():
			self.UpdateScrollbar(int((length * 0.01) * self.SCROLL_SPEED))
			return True
		
		return False
	
	def OnScrollBar(self, fScale):
		curr = min(0, max(math.ceil((self.scrollBoard.GetHeight() - self.peekWindow.GetHeight()) * fScale * -1.0), -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
	
	def ChangeScrollbar(self):
		if not self.scrollBar:
			return
		
		if self.scrollBoard.GetHeight() <= self.GetHeight():
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(self.GetHeight(), self.scrollBoard.GetHeight())
			self.scrollBar.SetPosScale(truediv(abs(self.scrollBoard.GetLocalPosition()[1]), (self.scrollBoard.GetHeight() - self.peekWindow.GetHeight())))
			self.scrollBar.Show()
	
	def UpdateScrollbar(self, val = 0):
		curr = min(0, max(self.scrollBoard.GetLocalPosition()[1] + val, -self.scrollBoard.GetHeight() + self.peekWindow.GetHeight()))
		self.scrollBoard.SetPosition(0, curr)
		
		self.ChangeScrollbar()
	
	def RegisterScrollBar(self):
		self.scrollBar = WikiScrollBar()
		self.scrollBar.SetParent(self)
		self.scrollBar.SetPosition(self.peekWindow.GetLocalPosition()[0] + self.peekWindow.GetWidth() + 1, self.peekWindow.GetLocalPosition()[1])
		self.scrollBar.SetSize(7, self.peekWindow.GetHeight())
		self.scrollBar.SetScrollEvent(self.OnScrollBar)
		self.scrollBar.SetScrollSpeed(self.SCROLL_SPEED)
		self.scrollBar.Show()
		
		self.ChangeScrollbar()

def InitMainWindow(self):
	self.AddFlag('movable')
	self.AddFlag('float')
	
	for i in ingamewikiconfig.ITEM_BLACKLIST:
		if type(i) == types.ListType:
			for k in i:
				wiki.RegisterItemBlacklist(k)
		else:
			wiki.RegisterItemBlacklist(i)
	
	for i in ingamewikiconfig.MOB_BLACKLIST:
		if type(i) == types.ListType:
			for k in i:
				wiki.RegisterMonsterBlacklist(k)
		else:
			wiki.RegisterMonsterBlacklist(i)
	
	nonplayer.BuildWikiSearchList()

def InitMainWeaponWindow(self):
	self.mainWeaponWindow = WikiMainWeaponWindow()
	self.mainWeaponWindow.SetParent(self.baseBoard)
	self.mainWeaponWindow.AddFlag("attach")
	self.mainWeaponWindow.SetPosition(*mainBoardPos)

def InitMainChestWindow(self):
	self.mainChestWindow = WikiMainChestWindow()
	self.mainChestWindow.SetParent(self.baseBoard)
	self.mainChestWindow.AddFlag("attach")
	self.mainChestWindow.SetPosition(*mainBoardPos)

def InitMainBossWindow(self):
	self.mainBossWindow = WikiMainBossWindow()
	self.mainBossWindow.SetParent(self.baseBoard)
	self.mainBossWindow.AddFlag("attach")
	self.mainBossWindow.SetPosition(*mainBoardPos)

def InitCustomPageWindow(self):
	self.customPageWindow = SimpleTextLoader()
	self.customPageWindow.SetParent(self.baseBoard)
	self.customPageWindow.AddFlag("attach")
	self.customPageWindow.SetPosition(*mainBoardPos)
	self.customPageWindow.Show()

def InitCostumePageWindow(self):
	self.costumePageWindow = WikiMainCostumeWindow()
	self.costumePageWindow.SetParent(self.baseBoard)
	self.costumePageWindow.AddFlag("attach")
	self.costumePageWindow.SetPosition(*mainBoardPos)

def InitTitleBar(self):
	self.titleBar = ui.TitleBar()
	self.titleBar.SetParent(self.baseBoard)
	self.titleBar.MakeTitleBar(0, "red")
	self.titleBar.SetWidth(self.GetWidth() - 15)
	self.titleBar.SetPosition(8, 7)
	self.titleBar.SetCloseEvent(self.Close)
	self.titleBar.Show()
	
	self.titleName = ui.TextLine()
	self.titleName.SetParent(self.titleBar)
	self.titleName.SetPosition(0, 4)
	self.titleName.SetPosition(0, 4)
	self.titleName.SetWindowHorizontalAlignCenter()
	self.titleName.SetHorizontalAlignCenter()
	self.titleName.SetText(localeInfo.WIKI_TITLENAME)
	self.titleName.Show()

def BuildSearchWindow(self):
	self.searchBG = ui.ExpandedImageBox()
	self.searchBG.SetParent(self.baseBoard)
	self.searchBG.LoadImage("d:/ymir work/ui/wiki/searchfield.tga")
	self.searchBG.SetPosition(13, 33)
	self.searchBG.Show()
	
	self.searchButton = ui.Button()
	self.searchButton.SetParent(self.searchBG)
	self.searchButton.SetUpVisual("d:/ymir work/ui/wiki/button_search_normal.tga")
	self.searchButton.SetOverVisual("d:/ymir work/ui/wiki/button_search_hover.tga")
	self.searchButton.SetDownVisual("d:/ymir work/ui/wiki/button_search_down.tga")
	self.searchButton.SetPosition(self.searchBG.GetWidth() - self.searchButton.GetWidth() - 2, self.searchBG.GetHeight() / 2 - self.searchButton.GetHeight() / 2)
	self.searchButton.SAFE_SetEvent(self.StartSearch)
	self.searchButton.Show()
	
	self.searchEdit = ui.EditLine()
	self.searchEdit.SetParent(self.searchBG)
	self.searchEdit.SetMax(50)
	self.searchEdit.SetSize(111 - self.searchButton.GetWidth() - 2, 15)
	self.searchEdit.SetPosition(5, self.searchBG.GetHeight() / 2 - 15 / 2)
	self.searchEdit.SetOverlayText(localeInfo.WIKI_SEARCH_OVERLAY_TEXT)
	self.searchEdit.SetLimitWidth(self.searchEdit.GetWidth())
	self.searchEdit.SetEscapeEvent(ui.__mem_func__(self.OnPressNameEscapeKey))
	self.searchEdit.SetReturnEvent(ui.__mem_func__(self.StartSearch))
	self.searchEdit.SetUpdateEvent(ui.__mem_func__(self.Search_RefreshTextHint))
	self.searchEdit.SetTabEvent(ui.__mem_func__(self.Search_CompleteTextSearch))
	self.searchEdit.SetOutline()
	self.searchEdit.Show()
	
	self.searchEditHint = ui.TextLine()
	self.searchEditHint.SetParent(self.searchEdit)
	self.searchEditHint.SetPackedFontColor(grp.GenerateColor(1.0, 1.0, 1.0, 0.5))
	self.searchEditHint.Show()

def BuildBaseMain(self):
	self.baseBoard = ui.ExpandedImageBox()
	self.baseBoard.AddFlag("attach")
	self.baseBoard.SetParent(self)
	self.baseBoard.LoadImage("D:/Ymir Work/ui/wiki/bg.tga")
	self.baseBoard.SetWindowName("InGameWikiBoard")
	self.baseBoard.Show()
	
	self.SetSize(self.baseBoard.GetWidth(), self.baseBoard.GetHeight())
	
	self.header = ui.ExpandedImageBox()
	self.header.SetParent(self.baseBoard)
	self.header.SetPosition(149, 37)
	
	BuildSearchWindow(self)
	
	self.exactSearch = ui.InGameWikiCheckBox()
	self.exactSearch.SetParent(self.baseBoard)
	self.exactSearch.SetPosition(13, self.searchBG.GetLocalPosition()[1] + self.searchBG.GetHeight() + 5)
	self.exactSearch.SetTextInfo(localeInfo.WIKI_EXACT_SEARCH_TEXT)
	self.exactSearch.Show()
	
	self.categText = ui.TextLine()
	self.categText.SetParent(self.baseBoard)
	self.categText.SetPosition(13, self.searchBG.GetLocalPosition()[1] + self.searchBG.GetHeight() + 25)
	self.categText.SetText(localeInfo.WIKI_CATEGORIES_TITLE)
	self.categText.Show()
	
	self.categ = WikiCategories()
	self.categ.hideWindowsEvent = ui.__mem_func__(self.CloseBaseWindows)
	self.categ.SetParent(self.baseBoard)
	self.categ.AddFlag("attach")
	self.categ.SetPosition(13, 107)
	self.categ.Show()
	
	self.prevButt = ui.Button()
	self.prevButt.SetParent(self.baseBoard)
	self.prevButt.SetUpVisual("d:/ymir work/ui/wiki/btn_arrow_left_normal.tga")
	self.prevButt.SetOverVisual("d:/ymir work/ui/wiki/btn_arrow_left_hover.tga")
	self.prevButt.SetDownVisual("d:/ymir work/ui/wiki/btn_arrow_left_down.tga")
	self.prevButt.SetDisableVisual("d:/ymir work/ui/wiki/btn_arrow_left_down.tga")
	self.prevButt.SetPosition(self.categ.GetLocalPosition()[0], self.categ.GetLocalPosition()[1] + self.categ.GetHeight() + 5)
	self.prevButt.SAFE_SetEvent(self.OnPressPrevButton)
	self.prevButt.Show()
	self.prevButt.Disable()
	
	self.nextButt = ui.Button()
	self.nextButt.SetParent(self.baseBoard)
	self.nextButt.SetUpVisual("d:/ymir work/ui/wiki/btn_arrow_right_normal.tga")
	self.nextButt.SetOverVisual("d:/ymir work/ui/wiki/btn_arrow_right_hover.tga")
	self.nextButt.SetDownVisual("d:/ymir work/ui/wiki/btn_arrow_right_down.tga")
	self.nextButt.SetDisableVisual("d:/ymir work/ui/wiki/btn_arrow_right_down.tga")
	self.nextButt.SetPosition(self.categ.GetLocalPosition()[0] + self.categ.GetWidth() - self.nextButt.GetWidth(), self.categ.GetLocalPosition()[1] + self.categ.GetHeight() + 5)
	self.nextButt.SAFE_SetEvent(self.OnPressNextButton)
	self.nextButt.Show()
	self.nextButt.Disable()
	
	self.scrollBar = WikiScrollBar()
	self.scrollBar.SetParent(self.baseBoard)
	self.scrollBar.SetPosition(self.categ.GetLocalPosition()[0] + self.categ.GetWidth() + 5, self.categ.GetLocalPosition()[1])
	self.scrollBar.SetSize(7, categoryPeakWindowSize[1])
	self.scrollBar.Show()
	
	self.categ.RegisterScrollBar(self.scrollBar)
	
	InitTitleBar(self)
	InitMainWeaponWindow(self)
	InitMainChestWindow(self)
	InitMainBossWindow(self)
	InitCustomPageWindow(self)
	
	InitCostumePageWindow(self)
	funclist = [
		ui.__mem_func__(self.mainWeaponWindow.Show),
		ui.__mem_func__(self.mainChestWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.mainBossWindow.Show),
		ui.__mem_func__(self.customPageWindow.LoadFile),
		ui.__mem_func__(self.customPageWindow.LoadFile),
		ui.__mem_func__(self.costumePageWindow.Show),
		ui.__mem_func__(self.customPageWindow.LoadFile),
		ui.__mem_func__(self.customPageWindow.LoadFile),
	]
	
	for i in ingamewikiconfig.WIKI_CATEGORIES:
		ret = self.categ.AddCategory(i[0])
		for j in xrange(len(i[1])):
			ret.AddSubCategory(j, i[1][j])
		
		curr = ingamewikiconfig.WIKI_CATEGORIES.index(i)
		if curr < len(funclist):
			ret.clickEvent = funclist[curr]
	
	self.customPageWindow.LoadFile("landingpage.txt")
	self.header.SetEventWiki(ui.__mem_func__(self.GoToLanding), "mouse_click_down")
