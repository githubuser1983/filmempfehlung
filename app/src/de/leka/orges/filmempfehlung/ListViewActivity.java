package de.leka.orges.filmempfehlung;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

import android.app.Activity;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.content.Intent;


import java.io.StringReader;
import java.lang.Exception;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.CharacterData;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;


import org.w3c.dom.Attr;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.ErrorHandler;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import android.net.Uri;
import android.content.Intent;
import android.widget.AdapterView;
import android.view.View;


public class ListViewActivity extends Activity {
  
  private ListView mainListView ;
  private LazyAdapter listAdapter ;
  //private ArrayList<String> urlList;  
  private ArrayList<String> titleList; // = new ArrayList<String>();
  private ArrayList<String> imdbUrlList ; // = new ArrayList<String>();
  private ArrayList<String> tmdbUrlList ; //= new ArrayList<String>();
  private ArrayList<String> genresList ; //= new ArrayList<String>();
  private ArrayList<String> posterPathUrlList; // = new  ArrayList<String>();
  
  //static final String KEY_SONG = "movie"; // parent node
  static final String KEY_ID = "id";
  static final String KEY_TITLE = "title";
  static final String KEY_GENRES = "genres";
  static final String KEY_POSTER_PATH_URL = "posterPathUrl";
  /** Called when the activity is first created. */
  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.simplelistview);
    
   // get XML
   Intent intent = getIntent();
   String xmlString = intent.getStringExtra("xml"); 

   titleList = new ArrayList<String>();
   imdbUrlList = new ArrayList<String>();
   tmdbUrlList = new ArrayList<String>();
   genresList = new ArrayList<String>();
   posterPathUrlList = new  ArrayList<String>();
   
   //urlList = new ArrayList<String>();

   ArrayList<HashMap<String, String>> movieList = new ArrayList<HashMap<String, String>>();
   
   // parse xml:
   try {
   DocumentBuilder db = DocumentBuilderFactory.newInstance().newDocumentBuilder();
   InputSource is = new InputSource();
   is.setCharacterStream(new StringReader(xmlString));

    Document doc = db.parse(is);
    Node root = doc.getDocumentElement();   
    NodeList list = root.getChildNodes();
 
    
    /*
     *  
     * <imdb>
       <row rank="1" tid="tt0499549" title="Avatar - Aufbruch nach Pandora (2009)" url="http://www.imdb.com/title/tt0499549/" />
       <row rank="2" tid="tt1285016" title="The Social Network (2010)" url="http://www.imdb.com/title/tt1285016/" />
     */
    int rowCounter = 0;
    for (int i = 0; i < list.getLength(); i++)
    {
    	HashMap<String, String> mapForRow = new HashMap<String, String>();
		
		// adding each child node to HashMap key => value
		//mapForRow.put(KEY_ID, String.format("%s",i));
		
    	
        Node n = list.item(i);
        if (n instanceof Element && n.hasAttributes()) {
            NamedNodeMap attrs = n.getAttributes(); 

            mapForRow.put(KEY_ID, new Integer(rowCounter).toString());
            //test:
            //mapForRow.put(KEY_GENRES, new Integer(rowCounter).toString());
            for (int j = 0; j < attrs.getLength(); j++) {
               // todo:
               // mapForRow.put(attrName,attrVal); 
            	
               Attr attribute = (Attr) attrs.item(j);
               String attrName = attribute.getName();
               String attrVal = attribute.getValue();
               if(attrName.equals("rank"))
               {
            	   //mapForRow.put(KEY_ID, String.format("%s",Integer.parseInt(attrVal)-1));
               }
               
               if(attrName.equals("title"))
               {
            	 mapForRow.put(KEY_TITLE, attrVal);
                 //titleList.add(attribute.getValue());
               }
               if(attrName.equals("url"))
               {
                 //urlList.add(attribute.getValue());
                 // todo: unterscheiden zw. Imdb und Tmdb Links:
                 imdbUrlList.add(attrVal);
                 tmdbUrlList.add(attrVal);
                 // test:
                 mapForRow.put(KEY_GENRES, attrVal);
               }
               if(attrName.equals("imdbUrl"))
               {
            	   imdbUrlList.add(attrVal);
               }
               if(attrName.equals("tmdbUrl"))
               {
            	   tmdbUrlList.add(attrVal);
               }
               if(attrName.equals("genres"))
               {
            	   mapForRow.put(KEY_GENRES, attrVal);
            	   //genresList.add(attribute.getValue());
               }
               if(attrName.equals("posterPathUrl"))
               {
            	   mapForRow.put(KEY_POSTER_PATH_URL, attrVal);
            	   //posterPathUrlList.add(attribute.getValue());
               }

            }
        rowCounter += 1;
        movieList.add(mapForRow);
        }
        
    }
    } catch( Exception e)
    {
      titleList.add("Ein Fehler trat auf.");
    }
 
    // xml parsed

    // Find the ListView resource. 
    mainListView = (ListView) findViewById( R.id.mainListView );

    
    // Create ArrayAdapter using the planet list.
    listAdapter = new LazyAdapter(this,  movieList);
    
    
    // Set the ArrayAdapter as the ListView's adapter.
    mainListView.setAdapter( listAdapter );

    mainListView.setClickable(true);
    mainListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {

    @Override
    public void onItemClick(AdapterView<?> arg0, View arg1, int position, long arg3) {

      Object o = mainListView.getItemAtPosition(position);
      String url = ListViewActivity.this.imdbUrlList.get(position);
      Uri uriUrl = Uri.parse(url);
      Intent launchBrowser = new Intent(Intent.ACTION_VIEW, uriUrl);
      startActivity(launchBrowser);

  }
});

  }
}
