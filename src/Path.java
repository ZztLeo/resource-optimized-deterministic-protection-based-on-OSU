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

	public boolean[] getCommonSlots(){
		boolean[] slots = this.get(0).getSlots();
		for (Link link : this){
			boolean[] curLinkSlots = link.getSlots();
			for( int i = 0; i < slots.length; i++){
				slots[i] |= curLinkSlots[i];
			}
		}
		return slots;		
	}


	public int get_max_continuous_slots_num(){
		int max_num = 0;
		int temp_num = 0;
		boolean[] slots = this.getCommonSlots();
		for(int i=0; i<slots.length; i++){
			if(slots[i] == false){
				temp_num++;
				if(i==slots.length-1){
					if(temp_num > max_num){
						max_num = temp_num;
						temp_num = 0;
					}
				}else{
					continue;
				}
			}else{
				if(temp_num > max_num){
					max_num = temp_num;
					temp_num = 0;
				}else{
					temp_num = 0;
				}
			}
		}
		return max_num;

	}
	
	
	public int get_common_free_slots_num(){
		int num = 0;
		boolean[] slots = this.getCommonSlots();
		for(int i=0; i<slots.length; i++){
			if(slots[i] == false){
				num++;
			}else{
				continue;
			}
		}
		return num;
	}
	
	
	public static void main(String[] args){
		Path path = new Path(null);
		boolean[] slots = {false,true,false,false,true,false,true};
		int num = path.get_max_continuous_slots_num();
		System.out.println(num);
		
	}
	
}