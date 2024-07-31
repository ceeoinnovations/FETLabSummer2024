import pyvista, os
import FileManager as fm
import ansys.fluent.visualization.pyvista as pv
import ansys.fluent.core as pyfluent

class SimpleSim:
    #SimpleSim breaks the process of setting up, running and performing post-processing a PyFluent simulation down to very few steps. 
    #This naturally decreases the amount control the user has over details of the simulation, limiting their control to the simulation model, fluid material and inlet velocity.
    #Conversely, the process of streamlining the simulation significantly decreases the learning curve and difficult of access to a fluid dynamics simulator
    def __init__(self, file, model="laminar", velocity=0.1, material='air'):
        self.meshing = pyfluent.launch_fluent(precision='double', processor_count=4, mode='meshing')
        self.instance = self.meshing._base_meshing._fluent_connection._remote_instance.name.replace("instances/", "")
        self.solver = ''
        self.file = file
        self.inlet_vel = velocity
        self.model = model
        self.material = material
        
    def import_geometry(self):
        #Imports a .pmdb file existing in the workspace into the PyFluent workflow, considering it to be a watertight geometry
        self.meshing.workflow.InitializeWorkflow(WorkflowType='Watertight Geometry')
        self.meshing.workflow.TaskObject['Import Geometry'].Arguments = dict(FileName=self.file, LengthUnit='mm')
        self.meshing.workflow.TaskObject['Import Geometry'].Execute()

    def generate_mesh(self):
        #Generates a simple, uniform mesh, without any local region sizing
        #Considers the geometry to only be composed of fluid regions
        #Saves an isometric view of the mesh as a .png file
        self.meshing.workflow.TaskObject['Generate the Surface Mesh'].Execute()
        self.meshing.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=False)
        self.meshing.workflow.TaskObject['Describe Geometry'].Arguments = dict(SetupType='The geometry consists of only fluid regions with no voids')
        self.meshing.workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=True)
        self.meshing.workflow.TaskObject['Describe Geometry'].Execute()
        self.meshing.workflow.TaskObject['Update Boundaries'].Execute()
        self.meshing.workflow.TaskObject['Update Regions'].Execute()
        self.meshing.workflow.TaskObject['Generate the Volume Mesh'].Execute()
        self.meshing.tui.display.save_picture('mesh.png')
    
    def show_png(self,png_name):
        #Displays a .png file lies somewhere in the workspace 
        pl = pyvista.Plotter()
        if self.solver:
            graphics = self.solver.results.graphics
            if graphics.picture.use_window_resolution.is_active():
                graphics.picture.use_window_resolution = False
            graphics.picture.x_resolution = 1920
            graphics.picture.y_resolution = 1440
        file_path = fm.get_file_path(png_name) #search for the file in home directory
        file_path_without_home = file_path.replace('/home/jovyan/', '') #remove /home/jovyan/ from the path
        pl.add_background_image(file_path_without_home)
        pl.show(jupyter_backend='static')

    def setup_sim(self):
        #Assigns the previously defined parameters and applies them to the specific 
        #Such parameters include inlet velocity, outlet pressure (set to 0), model and fluid material
        self.solver.setup.general.units.set_units(quantity="length", units_name="mm")
        self.solver.setup.models.viscous.model = self.model
        self.solver.setup.boundary_conditions.velocity_inlet["inlet"].momentum.velocity = self.inlet_vel
        self.solver.setup.boundary_conditions.pressure_outlet["outlet"].momentum.gauge_pressure = 0
        if self.material != 'air':
            try:
                self.solver.tui.define.materials.copy("fluid", self.material)
                self.solver.setup.cell_zone_conditions.fluid["part-1"].material = self.material
                print(f'Fluid material changed to {self.material}.')
            except:
                print('Selected material not found. Running simulation using air.')

    def simulate(self):
        #Performs the simulation that was previously setup 
        self.solver.solution.initialization.hybrid_initialize()
        self.solver.solution.run_calculation.iterate(iter_count=100)

    def contours(self, field="velocity-magnitude", surface="symmetry-plane"):
        #Generates and plots a contour plot for a given field (velocity-magnitude, pressure etc...) over a pre-existing plane (2D) surface
       	graphics = pv.Graphics(self.solver)
        contour = graphics.Contours[field+"-contour"]
        contour.field = field
        contour.surfaces_list = [surface]
        contour.display()
            
    def contoursALT(self,field,plane_name):
        #Alternative function to contours() in case the ansys.pyfluent.visualization.pyvista module is not working. 
        #This method utilizes the basic pyvista module as well as Fluent tui commmands.
        #The downside to this method is a large decrease in resolution in comparison to the contours() function 
        object_name='contour-plot'
        self.solver.tui.display.objects.create(
            'contour',
            object_name,
            'filled?',
            'yes',
            'node-values?',
            'yes',
            'field',
            field,
            'surfaces-list',
            plane_name,
            '()',
            'coloring',
            'smooth',
            'quit',
        )
        self.solver.tui.display.objects.display(object_name)
        self.solver.tui.display.views.auto_scale()
        self.solver.tui.views.restore_view('front')
        self.solver.tui.display.save_picture(object_name+'.png')
        self.show_png(object_name+'.png')
        
    def xyplot(self, field="velocity-magnitude", surface="centerline"):
        #Generates and displays an xy-plot of a given field (velocity-magnitude, pressure etc...) vs position along a pre-existing line (1D) surface
        #In this case it is plotted along the positive x-axis of the surface, this can be changed below. 
        plot_name = surface + '-' + field
        try:
            fm.delete_file(plot_name + ".png")
        except:
            pass
        self.solver.results.plot.xy_plot[plot_name] = {}
        self.solver.results.plot.xy_plot[plot_name] = {
            "y_axis_function": field,
            "surfaces_list": [surface],
            "plot_direction": {"option": "direction-vector", "direction_vector": {"z_component": 0, "y_component": 0, "x_component": 1}}
        }
        self.solver.tui.display.objects.display(plot_name)
        self.solver.tui.display.save_picture(plot_name + '.png')
        pl = pyvista.Plotter()
        pl.add_background_image(self.instance + '/' + plot_name + '.png')
        pl.show(jupyter_backend='static')
        self.solver.tui.surface.delete_surface(surface)
