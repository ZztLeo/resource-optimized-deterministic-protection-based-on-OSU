import java.util.*;


/**
* @description: Construct a hash table with two keys
* @ClassName: DoubleHash.java
* @author Jeyton
* @Date 2022-3-30 22:23:20
* @version 1.00
*/
public class DoubleHash<K1, K2, V> extends HashMap<K1, HashMap<K2, V>>{
	
	private static final long serialVersionUID = 1L; //Default serial version ID 1L

	/**
	* Check if there is a corresponding value for the keys
	*     
	* @param Key1 the first key.
	* @param Key2 the Ssecond key.
	* @return  whether the double keys correspond to a value (T/F).
	*/
	public boolean containsKey(K1 key1, K2 key2){
		if(this.containsKey(key1)){
			if(this.get(key1).containsKey(key2)){
				return true;
			}
		}
		return false;
	}
	
	/**
	* Get the value of the key1 and key2
	*
	* @param Key1 the first key.
	* @param Key2 the second key.
	* @return  the value of key1 and key2.
	*/
	public V get(K1 key1, K2 key2){
		if(containsKey(key1, key2)){
			return super.get(key1).get(key2);
		}
		return null;
	}
	
	/**
	* Put the map of <key1 <key2 value>> 
	*
	* @param Key1 the first key.
	* @param Key2 the second key.
	* @return  previous value, or null if none.
	*/
	public V put(K1 key1, K2 key2, V value){
		if(this.containsKey(key1)){
			return this.get(key1).put(key2, value);
		}
		this.put(key1, new HashMap<K2, V>());
		this.get(key1).put(key2, value);
		return null;
	}
	
	/**
	* Get all value of hashmap
	*
	* @return  an arraylist of all values.
	*/
	public Collection<V> getValues(){
		Collection<V> allValues = new ArrayList<V>();
		for (K1 key1 : this.keySet()){
			allValues.addAll(super.get(key1).values());
		}
		return allValues;
	}
	
	/**
	* Count the number of key/value pairs in a hashMap
	*
	* @return  total count number of key/value pairs
	*/
	public int size(){
		int size = 0;
		for (K1 key1 : this.keySet()){
			size += this.get(key1).size();
		}
		return size;
	}
	
	/**
	* Print the value of doublehash map by lines
	*	
	*/
	public void print(){
		for (K1 key1 : this.keySet()){
			for (K2 key2 : this.get(key1).keySet()){
				System.out.println(this.get(key1, key2));
			}
		}
	}
	
	
	/**
	 * Main function for testing
	 * 
	 * @param args 
	 */
	public static void main(String[] args){
		DoubleHash<Integer, Integer, String> index = new DoubleHash<Integer, Integer, String>();
		index.put(1, 14, "a");
		index.put(1, 7, "b");
		index.put(2, 12, "c");
		index.put(2, 6, "d");
		index.print();
		System.out.println(index);
		Collection<String> collection = new ArrayList<String>();
		collection = index.getValues();
		System.out.println(collection);
		
		DoubleHash<Integer, Integer, Link> x = new DoubleHash<Integer, Integer, Link>();
		Link link = new Link(1,14,1);
		x.put(1, 14, link);

	}
	
}