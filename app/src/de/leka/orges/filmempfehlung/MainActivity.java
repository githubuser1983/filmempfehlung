package de.leka.orges.filmempfehlung;

import java.util.Arrays;
import java.util.ArrayList;
import java.io.ByteArrayOutputStream;
import java.lang.Exception;

import android.content.Intent;
import android.os.AsyncTask;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.app.ListFragment;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MenuInflater;
import android.os.Bundle;
import android.widget.ArrayAdapter;
import android.widget.ListAdapter;
import android.widget.Toast;
import de.leka.orges.filmempfehlung.DragSortListView;
import de.leka.orges.filmempfehlung.DragSortController;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.HttpStatus;

public class MainActivity extends FragmentActivity implements
RemoveModeDialog.RemoveOkListener,
DragInitModeDialog.DragOkListener,
EnablesDialog.EnabledOkListener
{

    private int mNumHeaders = 0;
    private int mNumFooters = 0;

    private int mDragStartMode = DragSortController.ON_DRAG;
    private boolean mRemoveEnabled = true;
    //private int mRemoveMode = DragSortController.FLING_REMOVE;
    private int mRemoveMode = DragSortController.CLICK_REMOVE;
    private boolean mSortEnabled = true;
    private boolean mDragEnabled = true;

    private String mTag = "dslvTag";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.test_bed_main);

        if (savedInstanceState == null) {
            getSupportFragmentManager().beginTransaction().add(R.id.test_bed, getNewDslvFragment(), mTag).commit();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.mode_menu, menu);
        return true;
    }

    @Override
    public void onRemoveOkClick(int removeMode) {
        if (removeMode != mRemoveMode) {
            mRemoveMode = removeMode;
            getSupportFragmentManager().beginTransaction().replace(R.id.test_bed, getNewDslvFragment(), mTag).commit();
        }
    }

    @Override
    public void onDragOkClick(int dragStartMode) {
        mDragStartMode = dragStartMode;
        DSLVFragment f = (DSLVFragment) getSupportFragmentManager().findFragmentByTag(mTag);
        f.getController().setDragInitMode(dragStartMode);
    }

    @Override
    public void onEnabledOkClick(boolean drag, boolean sort, boolean remove) {
        mSortEnabled = sort;
        mRemoveEnabled = remove;
        mDragEnabled = drag;
        DSLVFragment f = (DSLVFragment) getSupportFragmentManager().findFragmentByTag(mTag);
        DragSortListView dslv = (DragSortListView) f.getListView();
        f.getController().setRemoveEnabled(remove);
        f.getController().setSortEnabled(sort);
        dslv.setDragEnabled(drag);
    }

    private Fragment getNewDslvFragment() {
        DSLVFragmentClicks f = DSLVFragmentClicks.newInstance(mNumHeaders, mNumFooters);
        f.removeMode = mRemoveMode;
        f.removeEnabled = mRemoveEnabled;
        f.dragStartMode = mDragStartMode;
        f.sortEnabled = mSortEnabled;
        f.dragEnabled = mDragEnabled;
        return f;
    }

   private class RetrieveUrl extends AsyncTask<String,Void,String> {


    protected String sendHttpRequestAndGetResponseAsString(String URL)
    {
      HttpClient httpclient = new DefaultHttpClient();
      try{
         HttpResponse response = httpclient.execute(new HttpGet(URL));
         StatusLine statusLine = response.getStatusLine();
         if(statusLine.getStatusCode() == HttpStatus.SC_OK){
           ByteArrayOutputStream out = new ByteArrayOutputStream();
           response.getEntity().writeTo(out);
           out.close();
           String responseString = out.toString();
           return responseString;
         } else{
           //Closes the connection.
           response.getEntity().getContent().close();
           return String.format("%d", statusLine.getStatusCode());
           //throw new IOException(statusLine.getReasonPhrase());
         }
      } catch( Exception e)
      {
        return e.toString();
      }
    }

      protected String doInBackground(String... URL) {
        return  sendHttpRequestAndGetResponseAsString(URL[0]);
      }
    
      protected void onPostExecute(String message) {
        //Toast.makeText(TestBedDSLV.this, message, Toast.LENGTH_SHORT).show();
        Intent myIntent = new Intent(MainActivity.this, ListViewActivity.class);
        myIntent.putExtra("xml", message); //Optional parameters
        MainActivity.this.startActivity(myIntent);
      }
    }

 
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle item selection
        FragmentTransaction transaction;
        DSLVFragment f = (DSLVFragment) getSupportFragmentManager().findFragmentByTag(mTag);
        DragSortListView dslv = (DragSortListView) f.getListView();
        DragSortController control = f.getController();

        
        if(item.getItemId() == R.id.select_recommendation)
        {
            //RemoveModeDialog rdialog = new RemoveModeDialog(mRemoveMode);
            //rdialog.setRemoveOkListener(this);
            //rdialog.show(getSupportFragmentManager(), "RemoveMode");
            String message = f.getOrderedTidsAsString();
            String url = String.format("http://%s/ordered?items=%s;removed=%s;presented=%s;actions=%s",
            		                                                getResources().getString(R.string.url),
            		                                                f.getOrderedTidsAsString(),
            		                                                f.getRemovedTidsAsString(),
            		                                                f.getPresentedTidsAsString(),
            		                                                f.getActionsAsString()
            		                                                );
            //Toast.makeText(f.getActivity(),url ,Toast.LENGTH_SHORT).show();
            //message = sendHttpRequestAndGetResponseAsString(url);
            new RetrieveUrl().execute(url);
            //Toast.makeText(f.getActivity(), message, Toast.LENGTH_SHORT).show();
            return true;
        //case R.id.select_help:
            //DragInitModeDialog ddialog = new DragInitModeDialog(mDragStartMode);
            //ddialog.setDragOkListener(this);
            //ddialog.show(getSupportFragmentManager(), "DragInitMode");
        //    return true;
        }
            else {
        
            return super.onOptionsItemSelected(item);
        }
    }
}
