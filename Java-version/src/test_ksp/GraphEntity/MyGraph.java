package test_ksp.GraphEntity;

//图邻接表的表示法
public class MyGraph{
    public Point[] point;
    public int[] visted;
    public int numPoint;
    public int numEdeges;
    public MyGraph() {}
    public MyGraph(int numPoint,int numEdeges)
    {
        this.numPoint=numPoint;
        this.numEdeges=numEdeges;
        point=new Point[numPoint];  //初始化点集数组
        visted=new int[numPoint];
    }
    public void createMyGraph(MyGraph MyGraph,int numPoint,int numEdeges,int EdegesPoint[][])  //创建图
    {
        for(int i=0;i<numPoint;i++)
        {
            MyGraph.visted[i]=0;
            System.out.println("请输入第"+(i+1)+"顶点的数据:");
            MyGraph.point[i]=new Point(i);   //录入顶点的数据域
        }
        for(int i=0;i<numEdeges;i++)   //初始化边表,这里使用到了链表中间的头插法
        {

            System.out.println("请输入第"+(i+1)+"条边的两端顶点坐标：");
//            int p1=in.nextInt();
//            int p2=in.nextInt();


            EdegeNode a=new EdegeNode(EdegesPoint[i][1],EdegesPoint[i][2]);         //记录出度
            a.nextEdge=MyGraph.point[EdegesPoint[i][0]].firstArc;  //头插法
            MyGraph.point[EdegesPoint[i][0]].firstArc=a;
//   EdegeNode b=new EdegeNode(p2);         //记录出度
//   b.adjvex=i;                            //记录入度
//   b.nextEdge=MyGraph.point[p2].firstArc;
//   MyGraph.point[p2].firstArc=b;
        }
    }

    public void DFS(MyGraph MyGraph,int m)
    {
        EdegeNode a = null;                                                 //创建一个边表结点的引用
        MyGraph.visted[m]=1;                                                      //访问该顶点，将该顶点的标志设置未true
        System.out.println("第"+m+"个顶点的信息："+MyGraph.point[m].data);     //打印访问的顶点的数据域
        a=MyGraph.point[m].firstArc;
        while(a!=null)
        {
            if(MyGraph.visted[a.adjvex]==0)
                DFS(MyGraph,a.adjvex);
            a=a.nextEdge;//实际上像是一种遍历链表的行为
        }
    }


}