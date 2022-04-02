import java.io.*;
import java.util.*;


/**
* @description: Define a network model including nodes and links
* @ClassName: Network.java
* @author Jeyton
* @Date 2022-3-29 22:37:54
* @version 1.00
*/
public class Network implements Serializable{
	
	private static final long serialVersionUID = 1L; //Default serial version ID 1L
    public static DoubleHash<Integer, Integer, Link> index;
    public static DoubleHash<Integer, Integer, Link> reverseIndex;
	private int numNodes, numLinks;
	
	/**
	* Read the network topology file when constructing a Network instance
	* @param fileName Filename of the selected network topology file
	* @throws Exception
	*/
	public Network(String fileName) {
		
        index = new DoubleHash<Integer, Integer, Link>();
		reverseIndex = new DoubleHash<Integer, Integer, Link>();

		BufferedReader inputStream = null;
		// Read network topology file
		try {
			inputStream = new BufferedReader(new FileReader("src/topo_file/" + fileName));
			String line;
			while((line = inputStream.readLine()) != null){
				String[] temp = line.split("\\s+");
				int from = Integer.parseInt(temp[0]);
				int to = Integer.parseInt(temp[1]);
				int distance = Integer.parseInt(temp[2]);
			
				Link newLink = new Link(from, to, distance);
				index.put(from, to, newLink);
				reverseIndex.put(to, from, newLink);
			}
		} catch(Exception e){
			System.out.println(e);
		}

		numNodes = index.keySet().size(); //number of nodes in the network
		numLinks = index.size(); //number of links in the network
		
		
		//candidatePaths = new DoubleHash<Integer, Integer, ArrayList<Path>>();
		/*
		try{
            
			if(fileName == "nsf.txt"){
				inputStream = new BufferedReader(new FileReader("nsf_k_paths.txt"));
			}

			if(fileName == "usnet.txt"){
				inputStream = new BufferedReader(new FileReader("usnet_k_paths.txt"));
			}
			
			if(fileName == "cost239.txt"){
				inputStream = new BufferedReader(new FileReader("cost239_k_paths.txt"));
			}
						
			String line;
			while((line = inputStream.readLine()) != null){
				String[] token = line.split("\\s+");
				int numHops = token.length;
				int[] path = new int[numHops];
				for(int i = 0; i < numHops; i++){
					path[i] = Integer.parseInt(token[i]);
				}
				
				if(!candidatePaths.containsKey(path[0], path[numHops-1])){
					candidatePaths.put(path[0], path[numHops-1], new ArrayList<Path>());
				}
				candidatePaths.get(path[0], path[numHops-1]).add(new Path(path));
			}
		} catch (Exception e){
			System.out.println(e);
		}
		*/
		
        
	}

    public int getNumNodes(){
		return numNodes;
	}
	
	public int getNumLinks(){
		return numLinks;
    }

    public Link link(int from, int to){
		return index.get(from, to);
	}
	
	public Link reverseLink(int to, int from){
		return reverseIndex.get(to, from);
	}


	/**
	 * Main function for testing
	 * @param args 
	 */
    public static void main(String[] args){
		Network network = new Network("nsf.txt");
        network.getNumNodes();
		//System.out.println(network.getNumNodes());
        network.getNumLinks();
    }
}