import java.util.*;


/**
* @description: Generate service matrix including protected services and unprotected services
* @ClassName: Network.java
* @author Jeyton
* @Date 2022-3-29 22:37:54
* @version 1.00
*/
public class Service {

	private int id;
	private int source;
	private int destination;
	private int bandwidth;
	private int[] bandwidthSet = {2,100,500,1000,100000,250000};
	private double[] serviceProportion = {0.1,0.3,0.1,0.2,0.2,0.1};

	public List<Double[]> ProtectService(Network g, int pro_service_num, Random randomStream){
		List<Double[]> pro_service = new ArrayList<Double[]>();

		Random rand = new Random();

		for(int i = 0; i < pro_service_num; i++){
			int rand_src = rand.nextInt(g.getNumNodes());
			int rand_dst = rand.nextInt(g.getNumNodes());
			while(rand_src == rand_dst){
				rand_dst = rand.nextInt(g.getNumNodes());
			}
			double rand_reliability = rand.nextDouble();

			double[] pro_service_proporty = {i,rand_src,rand_dst,rand_reliability};

			pro_service.add(pro_service_proporty);
		}

		return pro_service;
	}	
	public static void main(String[] args){

	}
}