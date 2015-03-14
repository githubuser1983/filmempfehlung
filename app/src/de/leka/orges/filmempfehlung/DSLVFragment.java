package de.leka.orges.filmempfehlung;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.TreeMap;
import java.util.Random;
import java.util.TreeSet;

import android.support.v4.app.ListFragment;
import android.app.Activity;
import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.TextView;
import android.widget.Toast;



public class DSLVFragment extends ListFragment {

    ArrayAdapter<String> adapter;

    public String[] array;
    public ArrayList<String> list;
    public ArrayList<String> presented;
    public ArrayList<String> removed;
    public ArrayList<String> actions; // Holds the actions done by user: removing, draging in format: 1,2>3,5>1,4 meaning 1=removed, 2. positon dragged to 3. position etc
    public ArrayList<Integer> ordered;
    public String[] titles;
    public String[] tids;
    public String[] urls;
    public TreeMap<String,String> tidToTitle;
    public TreeMap<String,String> tidToUrl;
    public int numberOfSampledItems = 20;

    public String[] sample(String[] array, int n, Boolean sameOrder)
    {
      if(n >= array.length)
      {
        return array;
      }else
      {
         String[] newArray = new String[n];
         TreeSet<Integer> indices = new TreeSet<Integer>();
         TreeMap<Double,Integer> randomlySorted = new TreeMap<Double,Integer>();
         Random generator = new Random();
         for(int i =0; i < array.length; i++)
         {
           Double rnd = generator.nextDouble();
           while(randomlySorted.containsKey(rnd)) // make sure the random numbers are unique
           {
             rnd = generator.nextDouble();
           } 
           randomlySorted.put(rnd,i);
         }       
         int i = 0;
         for(Double rnd : randomlySorted.keySet())
         {
           if(i >= n)
           {
             break;
           }
           if(sameOrder)
           {
             indices.add(randomlySorted.get(rnd));
           } else
           {
             newArray[i] = array[(int) randomlySorted.get(rnd)];
           }
           i += 1;
         }
        if(sameOrder)
        {
          int k = 0;
          for(Integer j : indices)
          {
            newArray[k] = array[(int) j];
            k += 1;
          }
        }
         return newArray;
      }
    }

   public String toStr(ArrayList<Integer> arrlist)
   {
      String s = "";
      for(int i = 0; i < arrlist.size(); i++)
      {
        if(i == 0 )
        {
          s = String.format("%d",arrlist.get(i));
        } else
        {
          s += "," + String.format("%d",arrlist.get(i));
        }
      }
      return s;
   }
   
   public String toStr(String[] arr)
   {
      String s = "";
      for(int i = 0; i < arr.length; i++)
      {
        if(i == 0 )
        {
          s = arr[i];
        } else
        {
          s += "," + arr[i];
        }
      }
      return s;
   }

   // tt123,...,tt456 (User clicks on Filmempfehlung after removing and sorting)
   public String getOrderedTidsAsString()
   {
     String[]  newArr = new String[ordered.size()];
     for(int i = 0; i < ordered.size(); i++)
     {
       newArr[i] = array[ordered.get(i)];
     }
     return toStr(newArr);
   }
   
   // tt123,...,tt456 as string as they are presented to the user (all tids)
   public String getPresentedTidsAsString()
   {
	   return toStr(presented.toArray(new String[presented.size()]));
   }
   
   
   // tt12,..tt34 as string, those tids which user has removed 
   public String getRemovedTidsAsString()
   {
	   return toStr(removed.toArray(new String[removed.size()]));
   }
   
   // 1,2>3,5>1,4 : meaning: 1 removed, 2. position dropped to 3. position etc.
   public String getActionsAsString()
   {
	   return toStr(actions.toArray(new String[actions.size()]));
   }

   private void changeOrderOnDrop(int from , int to)
   {
	 actions.add(String.format("%s-%s",ordered.get(from),ordered.get(to)));
	 //String message = getActionsAsString();
	 //Toast.makeText(getActivity(),message,Toast.LENGTH_SHORT).show();
     Integer item = ordered.get(from);
     ordered.remove(from);
     ordered.add(to,item);
   }

    private void changeOrderOnRemove(int which)
    {
      actions.add(String.format("%s",ordered.get(which)));	
      
      //String message = String.format("which = %d, ordered = %s, removed=%s", which, toStr(ordered),getRemovedTidsAsString());
      //Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
      removed.add(presented.get((int) ordered.get(which)));
      
      ordered.remove(which);
      //message = String.format("which = %d, ordered = %s, removed=%s", which, toStr(ordered),getRemovedTidsAsString());
      //Toast.makeText(getActivity(), message, Toast.LENGTH_SHORT).show();
      
    }

    private DragSortListView.DropListener onDrop =
            new DragSortListView.DropListener() {
                @Override
                public void drop(int from, int to) {
                    if (from != to) {

                        String item = adapter.getItem(from);
                        adapter.remove(item);
                        adapter.insert(item, to);
                        changeOrderOnDrop(from,to);
                        // TEST:
                        //String message = String.format("from = %d, to = %d", from, to);
                        //message = toStr(ordered);
                        //Toast.makeText(getActivity(), toStr(ordered), Toast.LENGTH_SHORT).show();
                    }
                }
            };

    private DragSortListView.RemoveListener onRemove = 
            new DragSortListView.RemoveListener() {
                @Override
                public void remove(int which) {
                    adapter.remove(adapter.getItem(which));
                    changeOrderOnRemove(which);
                }
            };

    protected int getLayout() {
        // this DSLV xml declaration does not call for the use
        // of the default DragSortController; therefore,
        // DSLVFragment has a buildController() method.
        return R.layout.dslv_fragment_main;
    }
    
    /**
     * Return list item layout resource passed to the ArrayAdapter.
     */
    protected int getItemLayout() {
        /*if (removeMode == DragSortController.FLING_LEFT_REMOVE || removeMode == DragSortController.SLIDE_LEFT_REMOVE) {
            return R.layout.list_item_handle_right;
        } else */
    	if (removeMode == DragSortController.CLICK_REMOVE) {
            return R.layout.list_item_click_remove;
        } else {
            return R.layout.list_item_handle_left;
        }
    }

    private DragSortListView mDslv;
    private DragSortController mController;

    public int dragStartMode = DragSortController.ON_DOWN;
    public boolean removeEnabled = false;
    public int removeMode = DragSortController.FLING_REMOVE;
    public boolean sortEnabled = true;
    public boolean dragEnabled = true;

    public static DSLVFragment newInstance(int headers, int footers) {
        DSLVFragment f = new DSLVFragment();

        Bundle args = new Bundle();
        args.putInt("headers", headers);
        args.putInt("footers", footers);
        f.setArguments(args);

        //f.setListAdapter();

        return f;
    }

    public DragSortController getController() {
        return mController;
    }


    public TreeMap<String,String> putArraysInTreeMap(String[] keyArr, String[] valArr)
    {
       TreeMap<String,String> t = new TreeMap<String,String>();
       if(keyArr.length != valArr.length)
       {
         return null;
       }
       for(int i = 0; i < keyArr.length; i++)
       {
         t.put(keyArr[i], valArr[i]);
       }
       return t;
    }

    /**
     * Called from DSLVFragment.onActivityCreated(). Override to
     * set a different adapter.
     */
    public void setListAdapter() {
        //array = getResources().getStringArray(R.array.jazz_artist_names);
        
        array = getResources().getStringArray(R.array.tid);
        tids = getResources().getStringArray(R.array.tid);
        titles = getResources().getStringArray(R.array.title);
        urls = getResources().getStringArray(R.array.url);
        
        tidToTitle = putArraysInTreeMap(tids,titles);
        tidToUrl = putArraysInTreeMap(tids,urls);

        Boolean sameOrder = true;
        array = sample(array,numberOfSampledItems,true);
        list = new ArrayList<String>(numberOfSampledItems);
        actions = new ArrayList<String>();
        removed = new ArrayList<String>();
        presented = new ArrayList<String>();
        for(int i = 0; i < numberOfSampledItems; i++)
        {
          list.add(tidToTitle.get(array[i]));
          presented.add(array[i]);
        }
        ordered = new ArrayList<Integer>(numberOfSampledItems);
        for(int i = 0; i < numberOfSampledItems; i++)
        {
          ordered.add((Integer) i);
        }

        adapter = new ArrayAdapter<String>(getActivity(), getItemLayout(), R.id.text, list);
        setListAdapter(adapter);
        
    }

    /**
     * Called in onCreateView. Override this to provide a custom
     * DragSortController.
     */
    public DragSortController buildController(DragSortListView dslv) {
        // defaults are
        //   dragStartMode = onDown
        //   removeMode = flingRight
        DragSortController controller = new DragSortController(dslv);
        controller.setDragHandleId(R.id.drag_handle);
        controller.setClickRemoveId(R.id.click_remove);
        controller.setRemoveEnabled(removeEnabled);
        controller.setSortEnabled(sortEnabled);
        controller.setDragInitMode(dragStartMode);
        controller.setRemoveMode(removeMode);
        return controller;
    }


    /** Called when the activity is first created. */
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState) {
        mDslv = (DragSortListView) inflater.inflate(getLayout(), container, false);

        mController = buildController(mDslv);
        mDslv.setFloatViewManager(mController);
        mDslv.setOnTouchListener(mController);
        mDslv.setDragEnabled(dragEnabled);

        //setListAdapter();

        return mDslv;
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);

        mDslv = (DragSortListView) getListView(); 

        mDslv.setDropListener(onDrop);
        mDslv.setRemoveListener(onRemove);

        Bundle args = getArguments();
        int headers = 0;
        int footers = 0;
        if (args != null) {
            headers = args.getInt("headers", 0);
            footers = args.getInt("footers", 0);
        }

        for (int i = 0; i < headers; i++) {
            addHeader(getActivity(), mDslv);
        }
        for (int i = 0; i < footers; i++) {
            addFooter(getActivity(), mDslv);
        }

        setListAdapter();
    }


    public static void addHeader(Activity activity, DragSortListView dslv) {
        LayoutInflater inflater = activity.getLayoutInflater();
        int count = dslv.getHeaderViewsCount();

        TextView header = (TextView) inflater.inflate(R.layout.header_footer, null);
        header.setText("Header #" + (count + 1));

        dslv.addHeaderView(header, null, false);
    }

    public static void addFooter(Activity activity, DragSortListView dslv) {
        LayoutInflater inflater = activity.getLayoutInflater();
        int count = dslv.getFooterViewsCount();

        TextView footer = (TextView) inflater.inflate(R.layout.header_footer, null);
        footer.setText("Footer #" + (count + 1));

        dslv.addFooterView(footer, null, false);
    }

}
