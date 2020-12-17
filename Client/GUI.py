import sys
import os
from PySide import QtGui, QtCore
from PySide.QtCore import QFile, QTextStream, Qt

#todo : output the different pools selection in differents txt file and apply this to the farm
#todo : display somme errors pop up
#todo : grey out all unavailable blades and block them from selection
#todo : problem : what happen when the user make his selection but don't click on apply ? answere : revert the settings and reedit the txt file

class MyDialog(QtGui.QWidget):

    #user accounts
    user_list = ["mromani", "bmakki", "kcapricelucien", "raudras", "bgot", "aperrin", "nbaussois", "lflorean", "ithistedjorgensen", "lremy", "td"]
    mapping_user_team = {"mromani":"BACKSTAGE","bmakki":"BARNEY","kcapricelucien":"COCORICA", "raudras":"DIVE", "aperrin":"DREAMBLOWER", "nbaussois":"FROM_ABOVE", "":"GOOD_MORNING_KITTY", "lflorean":"GREEN", "bgot":"HAKAM", "ithistedjorgensen":"PIR_HEARTH", "lremy":"RELATIVITY", "td":"TEST_PIPE" }
    # list of other PC selected from different blades
    default_pool = "default"
    team_list = [default_pool, "BACKSTAGE", "BARNEY", "COCORICA", "DIVE", "DREAMBLOWER", "FROM_ABOVE", "GOOD_MORNING_KITTY", "GREEN", "HAKAM", "PIR_HEARTH", "RELATIVITY", "TEST_PIPE"]
    current_Team = "HAKAM"
    scroll_layout = None

    path = r"Datas/blade_liste.txt" #path of the blade list
    out_path = r"Datas/"+current_Team+".txt"
    PC_list = [] #list of all computers
    PC_by_pools = {}
    list_selection = []
    pool_widget_list = {}


    #list of selected blade and available blade
    PC_list_widget = None
    selected_list = None

    def __init__(self) :
        super(MyDialog,self).__init__()
        self.PC_by_pools = self.import_PC_list(self.path)
        print("PC_by_pools = "+str(self.PC_by_pools))
        user_input = self.display_user_window()
        print("user_input = "+str(user_input))
        if(user_input[1]==True):
            self.user = user_input[0]
            self.current_Team = self.mapping_user_team[self.user]
            if self.PC_by_pools.has_key(self.current_Team):
                self.list_selection = self.PC_by_pools[self.current_Team]
            else:
                self.list_selection = []
            self.initUI()

        self.out_path = r"Datas/" + self.current_Team + ".txt"
    def display_user_window(self):
        user_input = QtGui.QInputDialog()
        user_valid = False
        user_input_widget = QtGui.QInputDialog()
        while(not user_valid):
            user_input = user_input_widget.getText(self, "User Name", "username")
            if(user_input[0] in self.user_list or user_input[1]==False):
                user_valid = True
        return user_input
    def initUI(self):
        #pool selections and Layout
        pools_layout = QtGui.QHBoxLayout()
        self.scroll_layout = QtGui.QScrollArea(self)

        ###init the pools GUI
        for i in range(0,len(self.team_list)):
            #if self.default_pool not in self.PC_by_pools.keys()[i]:
            pool_name = self.team_list[i] #get current GUI name

            layout = QtGui.QVBoxLayout()
            #pool title
            text = QtGui.QLabel(pool_name)
            text.setAlignment(Qt.AlignCenter)
            #pool list widget
            pool_widget = QtGui.QListWidget(self)
            pool_widget.setFixedSize(130,150)
            #add datas to it
            if(self.PC_by_pools.has_key(pool_name)):
                pool_widget.addItems(self.PC_by_pools[pool_name])
            #saves thes datas in a buffer : the list of pool_widget
            self.pool_widget_list[pool_name]=pool_widget

            layout.addWidget(text)
            layout.addWidget(self.pool_widget_list[pool_name])
            pools_layout.addLayout(layout)

        ####selection lists layout####
        hbox = QtGui.QHBoxLayout()

        ####list of blades###
        blade_layout = QtGui.QVBoxLayout()
        self.PC_list_widget = QtGui.QListWidget(self)
        self.PC_list_widget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        blade_layout.addWidget(QtGui.QLabel("all blades"))
        blade_layout.addWidget(self.PC_list_widget)

        #print("self.PC_by_pools[self.default_pool] = "+self.PC_by_pools[self.default_pool])
        self.update_list(self.PC_list_widget,self.PC_list)
        ####selection list####
        selection_layout = QtGui.QVBoxLayout()
        self.selected_list = QtGui.QListWidget(self)
        self.selected_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        selection_layout.addWidget(QtGui.QLabel(self.current_Team))
        selection_layout.addWidget(self.selected_list)
        self.selected_list.addItems(self.list_selection)

        #####add and remove buttons####
        add_button = QtGui.QPushButton("Add")
        add_button.clicked.connect(self.add_blade_computer)
        rem_button = QtGui.QPushButton("Remove")
        rem_button.clicked.connect(self.remove_blade_computer)

        layout_button = QtGui.QVBoxLayout()
        layout_button.addStretch(1)
        layout_button.addWidget(add_button)
        layout_button.addWidget(rem_button)
        layout_button.addStretch(1)

        ####buttons add/remove####
        hbox.addLayout(blade_layout)
        hbox.addLayout(layout_button)
        hbox.addLayout(selection_layout)

        ####Apply Button####
        self.apply_button = QtGui.QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_changes)

        ####image label####
        img_path = r"C:\Users\Natspir\Documents\SVG\CleResolume2020\KernelCyberStreet\GrafNSK2.png"
        pixMap = QtGui.QPixmap(img_path)
        label = QtGui.QLabel()
        label.setPixmap(pixMap)
        label.setAlignment(Qt.AlignCenter)

        self.setGeometry(300, 300, 450, 450)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QtGui.QIcon('web.png'))
        test = False

        #main Layout
        main_layout = QtGui.QVBoxLayout()
        frame_layout = QtGui.QWidget()
        frame_layout.setLayout(pools_layout)
        self.scroll_layout.setWidget(frame_layout)
        main_layout.addWidget(self.scroll_layout)
        main_layout.addStretch(1)
        main_layout.addLayout(hbox)
        main_layout.addWidget(self.apply_button)
        main_layout.addWidget(label)
        self.setLayout(main_layout)
        self.update_available_blades()
        self.show()


    ###controller part
    def update_available_blades(self):
        #pour chq blades
        #si ils ne sont pas present dans la pool default ou si ils sont deja selectionnes
        #mettre leur valeur en gris
        """for blade in self.PC_list:
            if blade not in self.PC_by_pools[self.default_pool]: #if the blade is not in the default pool, make it unavailable
                items = self.PC_list_widget.findItems(blade, Qt.MatchExactly)
                if(len(items)>0):
                    item = items[0]
                    #row = self.PC_list_widget.row(item)
                    #item.setBackground(QtGui.QBrush(QtGui.QColor(60, 60, 65)))
                    #self.set_color(QtGui.QColor(60, 60, 65), row)
                    item.setFlags(~QtCore.Qt.ItemIsEnabled)
                """
        nb_pc_items=self.PC_list_widget.count()
        for i in range(0,nb_pc_items):
            if(self.PC_list_widget.item(i).text() not in self.PC_by_pools[self.default_pool]):
                self.PC_list_widget.item(i).setFlags(~QtCore.Qt.ItemIsEnabled)

                #get the widget list
                #get the good line
                #color it

    def add_blade_computer(self):
        #read text file, check if selection is available
        #write text file, handle if erros
        #update the view
        self.update_available_blades()
        selections = self.PC_list_widget.selectedItems()

        for i in selections:#range(0,len(selections)):
            if(len(self.selected_list.findItems(i.text(),Qt.MatchExactly))==0):
                self.selected_list.addItem(i.text())#].text())
                PC_row = self.PC_list_widget.row(i)
                #i.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                #i.setBackground(QtGui.QBrush(QtGui.QColor(255, 60, 65)))
                #i.setStyleSheet("{color:#FFFF00}")
                """self.PC_list_widget.setProperty("styleVariant", 1)
                self.PC_list_widget.style().unpolish(self.PC_list_widget)
                self.PC_list_widget.style().polish(self.PC_list_widget)
                self.PC_list_widget.update()"""
                print(PC_row)

        #read text file. Parse it again to make sur to get the last changes
        pools = self.parse_txt_file()
        #compare if the selection is available or not; if it's in the default pool, it available
        valid_selection = []
        invalid_selection = []
        for item in selections:
            blade = item.text()
            if (blade in pools[self.default_pool]):#remove selected blade from default pool to move it to the current pool
                valid_selection.append(blade)
                pools[self.default_pool].remove(blade)
                item.setFlags(~QtCore.Qt.ItemIsEnabled) #set the color of the row if active or not
            elif(pools.has_key(self.current_Team) and blade in pools[self.current_Team]): #reset current pool
                valid_selection.append(blade)
                #pools[self.current_Team].remove(blade)
            else:
                invalid_selection.append(blade)
        #edit the text file
        self.update_text_file(pools,valid_selection)
        if(len(invalid_selection)>0):
            msg = "unfortunately the following PC are not available : "
            for i in invalid_selection:
                msg += "\n - "+i
            msg+="\n dur mec !"

            #todo : display a pop up indicating the blade that havn't been added and why
            info = QtGui.QMessageBox()
            info.setText(msg)
            info.exec_()

    def update_text_file(self, new_pools, valid_selection):
        list_blades = []  # saves the datas in a buffer
        for pool in new_pools:
            print("self.current_Team = " + self.current_Team + " pool = " + pool)
            # if(pool not in self.current_Team): #rewrite the text file with all the pools
            for blade in new_pools[pool]:
                line = blade + " ; " + pool + "\n"
                list_blades.append(line)
        for blade in valid_selection:  # rewrite the current pool with the new selection
            line = blade + " ; " + self.current_Team + "\n"
            list_blades.append(line)
        # write the buffer in the saved file
        print("list_blades = " + str(list_blades))
        f = open(self.path, "w")
        f.writelines(list_blades)
        f.close()
        #should return true or false if success

    def parse_txt_file(self):
        f = open(self.path, "r")
        pools = {self.default_pool:[]}
        for line in f:
            if line!= '\n':
                line = line.replace('\n','') #remove the '\n' character
                line = line.replace(' ','') #remove spaces
                datas = line.split(';')

                #define the name of the pool to add the blade
                if(len(datas)>=2 and datas[1] in self.team_list): #if the datas has at least two value, the pool name is in the second value
                    pool_name = datas[1]
                else:
                    pool_name = self.default_pool
                new_blade = datas[0]
                #add the blade to the pool
                if(pools.has_key(pool_name)): #add it if the key already exist, create it if not
                    pools[pool_name].append(new_blade)
                else:
                    pools[pool_name] = [new_blade]
                    #else put the computer in the default pool
        f.close()
        return pools



    def remove_blade_computer(self):
            pools = self.parse_txt_file()
            selections = self.selected_list.selectedItems()
            for i in selections:#for all items of the selection
                row = self.selected_list.row(i) #get the row
                PC_items = self.PC_list_widget.findItems(i.text(),Qt.MatchExactly ) #get the equivalent item in the allPC selection
                PC_row = self.PC_list_widget.row(PC_items[0]) #get the row in the all_PC list
                self.PC_list_widget.item(PC_row).setFlags(QtCore.Qt.ItemIsEnabled)

                self.selected_list.takeItem(row) #remove from the selection
                print("PC_row = "+str(PC_row)+" i = "+str(i))
               # self.set_color(QtGui.QColor(25, 25, 25),PC_row)

                print("remove item")
                #update the current pool PC list
                pools[self.current_Team].remove(i.text())
                if(pools.has_key(self.default_pool)):
                    pools[self.default_pool].append(i.text())
                else:
                    pools[self.default_pool] = [i.text()]
            #set the new PC list with all the pools
            self.update_text_file(pools, [])

    def set_color(self, color, row):
        self.PC_list_widget.item(row).setBackground(QtGui.QBrush(QtGui.QColor(color)))

    def write_selection_as_output(self):
        """write the selection in a single text file to apply it to the render farm as a pool"""
        f = open(self.out_path, "w")
        selection = []
        for index in range(0, self.selected_list.count()):
            item = self.selected_list.item(index)
            line = item.text() + "\n"
            selection.append(line)
        f.writelines(selection)
        f.close()

    def apply_changes(self):
        self.write_selection_as_output()
        #update views
        self.PC_by_pools = self.parse_txt_file()
        print("self.PC_by_pools = "+str(self.PC_by_pools))
        self.update_lists_widgets()
        """for i in self.team_list:
            if(self.PC_by_pools.has_key(i)):
                self.update_list(self.pool_widget_list[self.default_pool], self.PC_by_pools[self.default_pool])"""
        #send changes to tractor
        self.send_tractor_cmd()
        #display success message
        info_win = QtGui.QMessageBox()
        info_win.setText("pool setted succefully ! ")
        info_win.exec_()

    def send_tractor_cmd(self):
        here = os.path.dirname(__file__)
        pool_path = here+"/"+self.out_path
        pool_path = pool_path.replace("/",os.sep)
        cmd = "artfx-tractor pool "+self.current_Team+" --file "+pool_path
        print "cmd = "+cmd
        #print("here = "+)
        os.system(cmd)

    def update_lists_widgets(self):
        for pool_name in self.team_list:
            if(self.PC_by_pools.has_key(pool_name)):
                print("update pool "+pool_name)
                pool_widget = self.pool_widget_list[pool_name]
                pool_widget.clear()
                pool_widget.addItems(self.PC_by_pools[pool_name])

    def update_list(self, list_widget, PCs):
        list_widget.clear()
        list_widget.addItems(PCs)

    ####model####
    def import_PC_list(self, path):
        self.PC_list=[]
        #get the blades grouped by pools
        pools = self.parse_txt_file()
        #put all the blade in a single array
        for pool in pools.keys():
            for blade in pools[pool]:
               self.PC_list.append(blade)

        return pools

####GUI Style#####
def GUI_style(app):
    """app.setStyle(
        'Fusion')  # Style needed for palette to work# Dark Palette (found on github, couldn't track the original author)default_palette = QPalette()
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QtGui.QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Text, Qt.white)
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(53, 53, 53))
    # dark_palette.setColor(QtGui.QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)"""
    """fileQss = QtCore.QFile(r"C:\Users\Natspir\Documents\Code\Python\ArtFX\PoolManager\Client\Datas\Obit\Obit.qss")
    qss = QtCore.QTextStream(fileQss)
    print("QSS = "+qss.readAll())
    app.setStyleSheet(qss.readAll())"""
    file_qss = open(".\Datas\Combinear\Combinear.qss")
    with file_qss:
        qss = file_qss.read()
        #print("QSS = "+qss)
        app.setStyleSheet(qss)

def main():
    app = QtGui.QApplication(sys.argv)
    GUI_style(app)

    #connect_dialog = user_connect_dialog()
    my_dialog = MyDialog()
    sys.exit(app.exec_())

    pass

if __name__ == '__main__':
    main()