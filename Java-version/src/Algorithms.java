import java.util.*;


/**
* @description: Design a hybrid service static planning algorithm
* @ClassName: Algorathms.java
* @author Jeyton
* @Date 2022-4-18 10:35:37
* @version 1.00
*/
public class Algorithms {
    
  
    
    
    

    public void shortestPath_Dijkstra(int src, int dst){
      //Path result = new Path(null);
      boolean[] used = new boolean[Network.getNumNodes()];//Traversal identifier array
      used[src] = true;//Node src has been traversed

      //Initialize traversal identifier array
      for(int i = 1; i < Network.getNumNodes(); i++) {
        used[i] = false;
      }

      for(int i = 1; i < Network.getNumNodes(); i++) {
        int min = Integer.MAX_VALUE;  //Temporarily store the shortest distance from src to i, and initialize it to the integer maximum value
        int k = 0;
        /*for(src: Network.index.get(src);; j++) { //Find the node with the smallest distance from src to other noded
          if(!used[j] && result[j] != -1 && min > result[j]) {
            min = result[j];
            k = j;
          }*/
      }
      
      int count = 0;
      Set<Integer> Set = Network.index.get(src).keySet();
      int adjMatrix[][] = new int[Set.size()][2];
      for(int i : Set){
        adjMatrix[count][0] = i;
        adjMatrix[count][1] = Network.index.get(src).get(i).getDistance();
        count ++;
      }
      for(int i=0; i < adjMatrix.length; i++){
        for(int j=0; j < adjMatrix[i].length; j++){
          System.out.println(adjMatrix[i][j]);
        }
      }
      

      //return result;
    }
    
    
    
    public static void main(String[] args){
		
		Network network = new Network("nsf.txt");
    Algorithms test = new Algorithms();
		
    test.shortestPath_Dijkstra(1, 2);
	}
}
