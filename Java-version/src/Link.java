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
	

	public static int total_bandwidth = 100000; //The total bandwidth of each link is 100Gbps
	
	public Link (int from, int to, int distance){
		this.from = from;
		this.to = to;
		this.distance = distance;
	}
	
	public Link (Link another){
		this.from = another.getFrom();
		this.to = another.getTo();
		this.distance = another.getDistance();
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