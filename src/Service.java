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
	private static Random rand = new Random();
	private int[] bandwidthSet = {2,100,500,1000,100000,250000};
	private double[] serviceProportion = {0.1,0.3,0.1,0.2,0.2,0.1};
	public double [][] pro_service;


	//Generate protected services matrix
	public void GenerateProtectService(Network g, int pro_service_num){

		pro_service = new double[pro_service_num][5];
		double[] pro_service_bandwidth = new double[pro_service_num];

		//Chose service bandwidth from the bandwidth set according to the service proportion
		int temp_length = 0;
		for(int i = 0; i < bandwidthSet.length; i++){
			
			Arrays.fill(pro_service_bandwidth, temp_length, (int)(temp_length + serviceProportion[i]*pro_service_num), bandwidthSet[i]);
			temp_length = temp_length + (int)(serviceProportion[i]*pro_service_num);
		}
		
		shuffle(pro_service_bandwidth);
		
		
		//Construct random protected service matrix
		for(int i = 0; i < pro_service_num; i++){
			int rand_src = rand.nextInt(g.getNumNodes());
			int rand_dst = rand.nextInt(g.getNumNodes());
			while(rand_src == rand_dst){
				rand_dst = rand.nextInt(g.getNumNodes());
			}
			double rand_reliability = rand.nextDouble();

			pro_service[i][0] = i;
			pro_service[i][1] = rand_src;
			pro_service[i][2] = rand_dst;
			pro_service[i][3] = pro_service_bandwidth[i];
			pro_service[i][4] = rand_reliability;
		}

	}	

	public static<T> void swap(double[] a, int i, int j){
        double temp = a[i];
        a[i] = a[j];
        a[j] = temp;
    }

	public static<T> void shuffle(double[] pro_service_bandwidth) {
        int length = pro_service_bandwidth.length;
        for ( int i = length; i > 0; i-- ){
            int randInd = rand.nextInt(i);
            swap(pro_service_bandwidth, randInd, i - 1);
        }
    }

	public static void main(String[] args){
		Network network = new Network("nsf.txt");
		Service prot_service = new Service();
		//double arry[][] = prot_service.ProtectService(network, 200);
		/*for(int i = 0; i < arry.length; i++){
			for(int j = 0; j < arry[i].length; j++){
				System.out.println(arry[i][j]);
			}
		}
		*/
	}
}