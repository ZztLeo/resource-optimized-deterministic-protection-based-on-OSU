import java.util.*;


/**
* @description: Generate service matrix including protected services and unprotected services
* @ClassName: Service.java
* @author Jeyton
* @Date 2022-04-16 11:32:51
* @version 1.00
*/
public class Service {

	private static Random rand = new Random();
	private int[] bandwidthSet = {2,100,500,1000,100000,250000};
	private double[] serviceProportion = {0.1,0.3,0.1,0.2,0.2,0.1};
	public double [][] pro_service;
	public double [][] unpro_service;


	/**
	 * Generate protected service matrix
	 * @param g network topology
	 * @param pro_service_num the number of protected services 
	 */
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

	/**
	 * Generate unprotected service matrix
	 * @param g network topology
	 * @param unpro_service_num the number of unprotected services 
	 */
	public void GenerateUnProtectService(Network g, int unpro_service_num){

		unpro_service = new double[unpro_service_num][4];
		double[] unpro_service_bandwidth = new double[unpro_service_num];

		//Chose service bandwidth from the bandwidth set according to the service proportion
		int temp_length = 0;
		for(int i = 0; i < bandwidthSet.length; i++){
			
			Arrays.fill(unpro_service_bandwidth, temp_length, (int)(temp_length + serviceProportion[i]*unpro_service_num), bandwidthSet[i]);
			temp_length = temp_length + (int)(serviceProportion[i]*unpro_service_num);
		}
		
		shuffle(unpro_service_bandwidth);
		
		
		//Construct random unprotected service matrix
		for(int i = 0; i < unpro_service_num; i++){
			int rand_src = rand.nextInt(g.getNumNodes());
			int rand_dst = rand.nextInt(g.getNumNodes());
			while(rand_src == rand_dst){
				rand_dst = rand.nextInt(g.getNumNodes());
			}

			unpro_service[i][0] = i;
			unpro_service[i][1] = rand_src;
			unpro_service[i][2] = rand_dst;
			unpro_service[i][3] = unpro_service_bandwidth[i];
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
		Service service = new Service();
		service.GenerateProtectService(network, 200);
		service.GenerateUnProtectService(network, 400);

		for(int i = 0; i < service.unpro_service.length; i++){
			for(int j = 0; j < service.unpro_service[i].length; j++){
				System.out.println(service.unpro_service[i][j]);
			}
		}
	}

}