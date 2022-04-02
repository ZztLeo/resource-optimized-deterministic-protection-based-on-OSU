import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Simulation{
	
	
	public static double trafficLoad;
	public static int simulationLength = 50000;
	public static int simulation_times = 20;
	
	public static Map<Integer, Integer> bandwidth_map_blocked_num = new HashMap<Integer, Integer>(); 
	
	public double getTrafficLoad(){
		return trafficLoad;
	}
			
	public void startSimulate(Network network, int simulatedLength, int simulation_id){
		EventTrace trace = new EventTrace(trafficLoad);
		EventTrace.setSimulatedLength(simulatedLength);
		
		//-------------2018---12---16--------
		for(int i=1; i<9; i++) {
			bandwidth_map_blocked_num.put(i, 0);
		}
		//-------------

		
		Event event;
		int countnumber = 0;
		while((event = trace.nextEvent()) != null){
			if(event.getType() == EventType.ARRIVE){
				countnumber++;
				if(countnumber%5000 ==0){
					Results.record_BW_CU_usage();
				}
				boolean provisionSuceess = Algorithms.provision(trace, event);
				
				if(!provisionSuceess){
					
					int required_bandwidth = event.request.bandwidth;
					int blocked_num = bandwidth_map_blocked_num.get(required_bandwidth);
					bandwidth_map_blocked_num.put(required_bandwidth, blocked_num+1);
					
					Results.num_of_blocked_connections++;
				}
				
			}
			
			if(event.getType() == EventType.DEPART){
				Algorithms.release(event.request);
			}
		}
//		System.out.println("blocked_num_in_step_1 global_optimization"+Results.num_of_no_DC_in_global_optimization);
//		System.out.println("blocked_num_in_step_2 global_optimization"+Results.blocked_num_in_step_2_of_global_optimization);
		
		//-------------2018---12---16--------
		for(int i=1; i<9; i++) {
			List<Integer> blocked_num_array= Results.bandwidth_map_block_connections_array.get(i);
			blocked_num_array.add(bandwidth_map_blocked_num.get(i));
			Results.bandwidth_map_block_connections_array.put(i,blocked_num_array);
		}
		
		
		Results.set_BW_CU_utilization_and_blocking_ratio_average_hops(simulation_id);
		Results.reset_for_next_simulation();
		
	}
		
	
	
	public static void main(String[] args){
		
		//store the topology resource and k shortest paths
		Network network = new Network("usnet.txt");
		Simulation simulation = new Simulation();
		
	
		for(double load = 600; load<=600; load=load+25){
			Simulation.trafficLoad = load;
			System.out.println("trafficLoad = " + trafficLoad + ";");
			
			for(int m=1; m<10; m=m+1){
				DataCenter.CU_cost_per_slot_per_vnf = m;
				System.out.println("CU/slot = " + m + ";");
				
				//---------------2018----12----16----
				for(int b=1; b<9; b++) {
					List<Integer> initial = new ArrayList<>();
					Results.bandwidth_map_block_connections_array.put(b, initial);
				}
				
				
				for(int i=0; i<simulation_times; i++){
					network.store_DC_locations();
//					network.generate_VNF_deployment_in_DCs();
					simulation.startSimulate(network, simulationLength, i);
					network.reset();
				}

				Results.print_final_results();
				System.out.println("---------------------");

			}
			
		}
		
	}
	
}