package de.leka.orges.filmempfehlung;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class DBHelper extends SQLiteOpenHelper {
		 
	    // Logcat tag
	    private static final String LOG = "DBHelper";
	 
	    // Database Version
	    private static final int DATABASE_VERSION = 1;
	 
	    // Database Name
	    private static final String DATABASE_NAME = "filmempfehlung.db";
	 
	    // Table Names
		private static final String TABLE_ITEM_ID = "item";
		private static final String TABLE_ITEM_IN_LIST = "itemInList";
		private static final String TABLE_LIST_OF_ITEMS = "listOfItem";
	 
	 
	    // Table Create Statements
	    // Todo:
		// sql create statements in eine einzelne Datei einfuegen, damit es leichter zu pflegen ist, und diese dann hier einlesen
		
		/*
		
		insert into item(_id,tid,title,url) values (0,'t1','title1','url1'),(1,'t2','title2','url2'),(2,'t3','title3','url3'),(3,'t4','title4','url4');
		insert into listOfItem(_id,title,subtitle,created,updated) values (0,'list1','mylist1','2014-09-12','2014-09-12'),(1,'list2','mylist2','2014-09-13','2014-09-13');
		insert into itemInList(_id,listId,position,itemId) values (0,0,0,0), (1,0,1,2),(2,1,0,3),(3,1,1,2),(4,1,2,0);
		
		
		# "allLists":
		# listId, listTitle, listSubTitle, listCreated, listUpdated, listPosition, itemId, itemTitle, itemUrl
		select l._id as listId, l.title as listTitle, l.subtitle as listSubTitle, l.created as listCreated, l.updated as listUpdated, il.position as listPosition, i._id as itemId, i.tid as itemTid, i.title as itemTitle ,i.url as itemUrl from listOfItem l, itemInList il, item i where il.listId = l._id and il.itemId = i._id;
		
		
		*/

		// tabellen werden in der reihenfolge erzeugt, wie sie hier auftauchen:
	    private static final String[] CREATE_TABLES = new String[] 
	    		{ 
	    	      "create table item ( _id integer primary key autoincrement, tid varchar(20), title varchar(100), url varchar(200));", 
	    	      "create table listOfItem (_id integer primary key autoincrement, title varchar(100), subtitle varchar(300), created datetime, updated datetime);",
	    	      "create table itemInList (_id integer primary key autoincrement, listId integer, position integer auto increment, itemId integer,  FOREIGN KEY(listId) REFERENCES listOfItem(_id) on delete cascade, foreign key(itemId) references item(_id) on delete cascade);"
	    	      };
	    
	    			 
	    public DBHelper(Context context) {
	        super(context, DATABASE_NAME, null, DATABASE_VERSION);
	    }
	 
	    @Override
	    public void onCreate(SQLiteDatabase db) 
	    {
	 
	    	for(String createTable : CREATE_TABLES)
	    	{
	        // creating required tables
	          db.execSQL(createTable);
	    	}
	    }
	    
	 
	    @Override
	    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
	        // erstmal nix machen! 
	    	// todo: skripte schreiben wie oben, die ausgefuehrt werden, wenn es ein neues schema gibt, etwa so:
	    	// 1. neue Tabellen erstellen.
	    	// 2. Daten von den alten Tabellen in die neuen Tabellen kopieren.
	    	// 3. alte Tabellen loeschen.
	    }
	    
	    // insert and delete items
	    
	    // insert and delete listOfItem
	    // update title, subTitle of one listOfItem
	    
	    // itemInList:
	    //   support here methods from Java-ArrayList
	    //   given a listId peform:
	    //      get(listId,position) -> returns itemId at position
	    //      add(listId,position,itemId) -> puts itemId at position in listId (listId does not have to exist)
	    //      add(listId,itemId) -> puts itemId at last position
	    //      delete(listId,position)
	
}
