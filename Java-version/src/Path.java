import java.util.*;


/**
* @description: Define a network model including nodes and links
* @ClassName: Path.java
* @author Jeyton
* @Date 2022-4-13 22:11:36
* @version 1.00
*/
public class Path extends ArrayList<Link>{
	
	private static final long serialVersionUID = 1L;

	public Path(int[] path){
		
		for(int i = 0; i < path.length-1; i++){
			this.add(Network.index.get(path[i], path[i+1]));
		}
		
	}
	
	public void printPath(Path path){
		System.out.print("the route is ");
		for(int i = 0; i < path.size(); i++){
			System.out.print(path.get(i).getFrom() + "--");
		}
		System.out.print(path.get(path.size()-1).getTo());
		System.out.println("");
	}

	
	
	public static void main(String[] args){
		Path path = new Path(null);
		boolean[] slots = {false,true,false,false,true,false,true};
				
	}
	
}