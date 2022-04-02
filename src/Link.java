import java.io.Serializable;
import java.util.*;


/**
* @description: Define a network link model including source(from), destination(to) and 
* @ClassName: Link.java
* @author Jeyton
* @Date 2022-3-30 10:57:06
* @version 1.00
*/
public class Link implements Serializable {

	private static final long serialVersionUID = 1L; //Default serial version ID 1L
	private int from;
	private int to;
	private int distance;
	private boolean[] slots;
	//public static int numSlots = 320;
	
	public Link (int from, int to, int distance){
		this.from = from;
		this.to = to;
		this.distance = distance;
	}
	
	public Link (Link another){
		this.from = another.getFrom();
		this.to = another.getTo();
		this.distance = another.getDistance();
		this.slots = another.getSlots();
	}
	
	public int getFrom(){
		return from;
	}
	
	public int getTo(){
		return to;
	}
	
	public int getDistance(){
		return distance;
	}
	
	public boolean[] getSlots(){
		boolean[] slotsCopy = new boolean[slots.length];
		System.arraycopy(slots, 0, slotsCopy, 0, slots.length);
		return slotsCopy;
	}
	
	public void reset(){
		for (int i=0; i<slots.length; i++){
			slots[i] = false;
		}
	}
	
	public void setSlots(boolean[] slots){
		System.arraycopy(slots, 0, this.slots, 0, slots.length);
	}	
	
	public int get_free_slot_num(){
		int num=0;
		for(int i=0; i<slots.length; i++){
			if(slots[i] == false){
				num = num+1;
			}
		}
		return num;
	}
	
	
	public int get_max_continuous_slots_num(){
		int max_num = 0;
		int temp_num = 0;
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
	
	
	public void mask(boolean[] slots) {
		for (int i=0; i<slots.length; i++) {
			this.slots[i] |= slots[i];
		}
	}
	
	public void unmask(boolean[] slots) {
		for (int i=0; i<slots.length; i++) {
			this.slots[i] &= (!slots[i]);
		}
	}
	

	/**
	 * Main function for testing
	 * 
	 * @param args 
	 */
	public static void main(String[] args){
		Link a = new Link(1,14,1);
		Link b = new Link(a);
		List<Link> linkList = new ArrayList<Link>();
		linkList.add(a);
		linkList.add(b);
		
	}
}