import app, item, nonplayer, ui, ingamewikiui,\
 wiki, wndMgr, grp

class InGameWiki(ui.Window):
	def __init__(self):
		self.searchEdit = None
		
		ui.Window.__init__(self)
		
		self.SetWindowName("InGameWiki")
		wiki.RegisterClass(self)
		
		self.objList = {}
		self.windowHistory = []
		self.currSelected = 0
		
		self.BuildUI()
		self.SetCenterPosition()
		self.Hide()
	
	def __del__(self):
		wiki.UnregisterClass()
		
		ui.Window.__del__(self)
	
	def Show(self):
		wndMgr.Show(self.hWnd)
		
		wiki.ShowModelViewManager(True)
	
	def Hide(self):
		wndMgr.Hide(self.hWnd)
		
		wiki.ShowModelViewManager(False)
		
		if self.searchEdit:
			self.searchEdit.KillFocus()
	
	def Close(self):
		self.Hide()
	
	def OnPressEscapeKey(self):
		self.Close()
		return True
	
	def BINARY_LoadInfo(self, objID, vnum):
		if objID in self.objList:
			self.objList[objID].NoticeMe()
	
	def BuildUI(self):
		ingamewikiui.InitMainWindow(self)
		ingamewikiui.BuildBaseMain(self)
	
	def OpenSpecialPage(self, oldWindow, vnum, isMonster = False):
		del self.windowHistory[self.currSelected + 1:]
		
		try:
			if oldWindow:
				del self.windowHistory[:]
				
				self.currSelected = 0
				self.windowHistory.append(oldWindow)
			
			if len(self.windowHistory) > 0:
				self.windowHistory[-1].Hide()
			
			newSpec = ingamewikiui.SpecialPageWindow(vnum, isMonster)
			newSpec.AddFlag("attach")
			newSpec.SetParent(self)
			newSpec.SetPosition(ingamewikiui.mainBoardPos[0] + 7, ingamewikiui.mainBoardPos[1] + 7)
			newSpec.Show()
			
			self.windowHistory.append(newSpec)
			self.currSelected = self.windowHistory.index(newSpec)
			
			self.prevButt.Enable() if self.currSelected > 0 else self.prevButt.Disable()
			self.nextButt.Disable()
		except ReferenceError:
			pass
	
	def OnPressNameEscapeKey(self):
		if not self.searchEdit:
			return
		
		if not self.searchEdit.IsShowCursor() or self.searchEdit.GetText() == "":
			self.OnPressEscapeKey()
		else:
			self.searchEdit.SetText("")
			self.searchEditHint.SetText("")
	
	def Search_RefreshTextHint(self):
		EDIT_TEXT_BASE_COLOR = grp.GenerateColor(0.8549, 0.8549, 0.8549, 1.0)
		EDIT_TEXT_NOT_FOUND_COLOR = grp.GenerateColor(1.0, 0.2, 0.2, 1.0)
		
		self.searchEditHint.SetText("")
		self.searchEdit.SetPackedFontColor(EDIT_TEXT_BASE_COLOR)
		
		search_text = self.searchEdit.GetText()
		
		if len(search_text):
			(hintName, vnum) = item.GetItemDataByNamePart(search_text)
			if vnum == -1:
				(hintName, vnum) = nonplayer.GetMonsterDataByNamePart(search_text)
				if vnum == -1:
					self.searchEditHint.SetText("")
					self.searchEdit.SetPackedFontColor(EDIT_TEXT_NOT_FOUND_COLOR)
				else:
					self.searchEditHint.SetText(search_text + " " + hintName[len(search_text):])
			else:
				self.searchEditHint.SetText(search_text + " " + hintName[len(search_text):])
	
	def OnUpdate(self):
		(start, end) = self.searchEdit.GetRenderPos()
		self.searchEditHint.SetFixedRenderPos(start, end) if start else self.searchEditHint.SetFixedRenderPos(start, 17)
	
	def Search_CompleteTextSearch(self):
		if self.searchEditHint.GetText():
			oldText = self.searchEdit.GetText()
			self.searchEdit.SetText(oldText + self.searchEditHint.GetText()[len(oldText)+1:])
			self.searchEdit.SetEndPosition()
			self.Search_RefreshTextHint()
	
	def StartSearch(self):
		
		def check_exact_search(real_name, check_name):
			if not self.exactSearch.GetCheckStatus():
				return True
			
			if real_name.lower() != check_name.lower():
				return False
			
			return True
		
		search_text = self.searchEdit.GetText()
		if len(search_text):
			(search_name, search_vnum) = item.GetItemDataByNamePart(search_text)
			if search_vnum == -1 or not check_exact_search(search_name, search_text):
				(search_name, search_vnum) = nonplayer.GetMonsterDataByNamePart(search_text)
				if search_vnum == -1 or not check_exact_search(search_name, search_text):
					return
				
				self.CloseBaseWindows()
				self.OpenSpecialPage(None, search_vnum, True)
			else:
				self.CloseBaseWindows()
				
				item.SelectItem(search_vnum)
				checkedVnum = ((int(search_vnum / 10) * 10) if wiki.CanIncrRefineLevel() else search_vnum)
				self.OpenSpecialPage(None, checkedVnum, False)
	
	def GoToLanding(self):
		self.CloseBaseWindows()
		self.categ.NotifyCategorySelect(None)
		self.customPageWindow.LoadFile("landingpage.txt")
	
	def OnPressNextButton(self):
		if len(self.windowHistory) - 1 > self.currSelected:
			self.windowHistory[self.currSelected].Hide()
			self.currSelected += 1
			self.windowHistory[self.currSelected].OpenWindow()

			self.prevButt.Enable()
			if len(self.windowHistory) - 1 == self.currSelected:
				self.nextButt.Disable()
	
	def OnPressPrevButton(self):
		if self.currSelected > 0:
			self.windowHistory[self.currSelected].Hide()
			self.currSelected -= 1
			self.windowHistory[self.currSelected].OpenWindow()
			
			self.nextButt.Enable()
			if self.currSelected == 0:
				self.prevButt.Disable()
	
	def CloseBaseWindows(self):
		self.mainWeaponWindow.Hide()
		self.mainChestWindow.Hide()
		self.mainBossWindow.Hide()
		self.customPageWindow.Hide()
		self.costumePageWindow.Hide()
		
		del self.windowHistory[:]
		self.prevButt.Disable()
		self.nextButt.Disable()
		self.currSelected = 0
